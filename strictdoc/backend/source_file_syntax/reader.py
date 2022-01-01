import sys
import traceback
from functools import partial

from textx import metamodel_from_str, get_location

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.source_file_syntax.grammar import SOURCE_FILE_GRAMMAR
from strictdoc.backend.source_file_syntax.models.range_pragma import RangePragma
from strictdoc.backend.source_file_syntax.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.helpers.string import get_lines_count
from strictdoc.helpers.textx import drop_textx_meta


class Req:
    def __init__(self, parent, uid):
        self.parent = parent
        self.uid = uid

        self.ng_source_line = None
        self.ng_source_column = None


class ParseContext:
    def __init__(self, lines_total):
        self.lines_total = lines_total
        self.pragmas = []
        self.pragma_stack = []
        self.map_lines_to_pragmas = {}
        self.map_reqs_to_pragmas = {}


def req_processor(req: Req):
    assert isinstance(
        req, Req
    ), f"Expected req to be Req, got: {req}, {type(req)}"
    location = get_location(req)
    assert location
    req.ng_source_line = location["line"]
    req.ng_source_column = location["col"]


def source_file_traceability_info_processor(
    source_file_traceability_info: SourceFileTraceabilityInfo,
    parse_context: ParseContext,
):
    source_file_traceability_info.pragmas = parse_context.pragmas
    # Finding how many lines are covered by the requirements in the file.
    # Quick and dirty: https://stackoverflow.com/a/15273749/598057
    merged_ranges = []
    for pragma in source_file_traceability_info.pragmas:
        if not pragma.is_begin():
            continue
        begin, end = pragma.ng_range_line_begin, pragma.ng_range_line_end
        if merged_ranges and merged_ranges[-1][1] >= (begin - 1):
            merged_ranges[-1][1] = max(merged_ranges[-1][1], end)
        else:
            merged_ranges.append([begin, end])
    coverage = 0
    for merged_range in merged_ranges:
        coverage += merged_range[1] - merged_range[0] + 1
    source_file_traceability_info.set_coverage_stats(
        parse_context.lines_total, coverage
    )


def create_begin_end_range_reqs_mismatch_error(
    location, lhs_pragma_reqs, rhs_pragma_reqs
):
    lhs_pragma_reqs_str = ", ".join(lhs_pragma_reqs)
    rhs_pragma_reqs_str = ", ".join(rhs_pragma_reqs)

    return StrictDocSemanticError(
        "STRICTDOC RANGE: BEGIN and END requirements mismatch",
        (
            "STRICT RANGE pragma should START and END "
            "with the same requirement(s): "
            f"'{lhs_pragma_reqs_str}' != '{rhs_pragma_reqs_str}'."
        ),
        # [nosdoc]
        """
# [REQ-001]
Content...
# [/REQ-001]
        """.lstrip(),
        # [/nosdoc]
        line=location["line"],
        col=location["col"],
        filename=location["filename"],
    )


def create_end_without_begin_error(location):
    return StrictDocSemanticError(
        "STRICTDOC RANGE: END pragma without preceding BEGIN pragma",
        (
            "STRICT RANGE shall be opened with "
            "START pragma and ended with END pragma."
        ),
        # [nosdoc]
        """
# [REQ-001]
Content...
# [/REQ-001]
        """.lstrip(),
        # [/nosdoc]
        line=location["line"],
        col=location["col"],
        filename=location["filename"],
    )


def range_start_pragma_processor(
    pragma: RangePragma, parse_context: ParseContext
):
    parse_context.pragmas.append(pragma)
    location = get_location(pragma)
    line = location["line"]
    pragma.ng_source_line_begin = line
    parse_context.map_lines_to_pragmas[line] = pragma

    if pragma.is_begin():
        pragma.ng_range_line_begin = line
        parse_context.pragma_stack.append(pragma)
        parse_context.map_lines_to_pragmas[line] = pragma
        for req in pragma.reqs:
            pragmas = parse_context.map_reqs_to_pragmas.setdefault(req, [])
            pragmas.append(pragma)

    elif pragma.is_end():
        try:
            current_top_pragma: RangePragma = parse_context.pragma_stack.pop()
            if pragma.reqs != current_top_pragma.reqs:
                raise create_begin_end_range_reqs_mismatch_error(
                    location, current_top_pragma.reqs, pragma.reqs
                )
            current_top_pragma.ng_range_line_end = line

            pragma.ng_range_line_begin = current_top_pragma.ng_range_line_begin
            pragma.ng_range_line_end = line

        except IndexError:
            raise create_end_without_begin_error(location) from None
    else:
        raise NotImplementedError


class SourceFileTraceabilityReader:
    SOURCE_FILE_MODELS = [Req, SourceFileTraceabilityInfo, RangePragma]

    def __init__(self):
        self.meta_model = metamodel_from_str(
            SOURCE_FILE_GRAMMAR,
            classes=SourceFileTraceabilityReader.SOURCE_FILE_MODELS,
            use_regexp_group=True,
        )

    def read(self, input_string, file_path=None):
        # TODO: This might be possible to handle directly in the textx grammar.
        # AttributeError: 'str' object has no attribute '_tx_parser'
        file_size = len(input_string)
        if file_size == 0:
            return SourceFileTraceabilityInfo([])

        length = get_lines_count(input_string)
        parse_context = ParseContext(length)

        parse_source_traceability_processor = partial(
            source_file_traceability_info_processor, parse_context=parse_context
        )
        parse_req_processor = partial(req_processor)
        parse_range_start_pragma_processor = partial(
            range_start_pragma_processor, parse_context=parse_context
        )

        obj_processors = {
            "Req": parse_req_processor,
            "SourceFileTraceabilityInfo": parse_source_traceability_processor,
            "RangePragma": parse_range_start_pragma_processor,
        }

        self.meta_model.register_obj_processors(obj_processors)

        try:
            source_file_traceability_info: SourceFileTraceabilityInfo = (
                self.meta_model.model_from_str(
                    input_string, file_name=file_path
                )
            )
            if source_file_traceability_info:
                source_file_traceability_info.ng_map_lines_to_pragmas = (
                    parse_context.map_lines_to_pragmas
                )
                source_file_traceability_info.ng_map_reqs_to_pragmas = (
                    parse_context.map_reqs_to_pragmas
                )

        except StrictDocSemanticError as exc:
            raise exc

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(source_file_traceability_info)
        return source_file_traceability_info

    def read_from_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                sdoc_content = file.read()
                sdoc = self.read(sdoc_content, file_path=file_path)
                return sdoc
        except NotImplementedError:
            traceback.print_exc()
            sys.exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(
                f"error: SourceFileTraceabilityReader: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided
            # traceback.print_exc()
            sys.exit(1)
