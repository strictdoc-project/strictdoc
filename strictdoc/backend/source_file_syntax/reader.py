import os
import traceback
from functools import partial

from textx import metamodel_from_str, get_location

from strictdoc.backend.dsl.error_handling import StrictDocSemanticError
from strictdoc.backend.source_file_syntax.grammar import SOURCE_FILE_GRAMMAR


class SourceFileTraceabilityInfo:
    def __init__(self, pragmas):
        self.pragmas = pragmas
        self.ng_map_lines_to_pragmas = {}
        self.ng_map_reqs_to_pragmas = {}

        self._ng_lines_total = 0
        self._ng_lines_covered = 0
        self._coverage = 0

    def __str__(self):
        return (
            "SourceFileTraceabilityInfo("
            f"lines_total: {self._ng_lines_total}\n"
            f"lines_covered: {self._ng_lines_covered}\n"
            f"coverage: {self._coverage}\n"
            f"pragmas: {self.pragmas}\n"
            ")"
        )

    @property
    def coverage(self):
        return self._coverage

    def set_coverage_stats(self, lines_total, lines_covered):
        self._ng_lines_total = lines_total
        self._ng_lines_covered = lines_covered
        self._coverage = round(lines_covered / lines_total * 100, 1)


class RangePragma:
    def __init__(self, parent, pragma_type, begin_or_end, reqs):
        self.parent = parent
        self.pragma_type = pragma_type
        self.begin_or_end = begin_or_end
        self.reqs = reqs

        self.ng_source_line_begin = None
        self.ng_source_line_end = None

    def __str__(self):
        return (
            f"RangePragma("
            f"begin_or_end: {self.begin_or_end}, "
            f"ng_source_line_begin: {self.ng_source_line_begin}, "
            f"ng_source_line_end: {self.ng_source_line_end}, "
            f"reqs: {self.reqs}"
            f")"
        )

    def __repr__(self):
        return self.__str__()


class ParseContext:
    def __init__(self, lines_total):
        self.lines_total = lines_total
        self.pragma_stack = []
        self.map_lines_to_pragmas = {}
        self.map_reqs_to_pragmas = {}


def source_file_traceability_info_processor(
    source_file_traceability_info: SourceFileTraceabilityInfo,
    parse_context: ParseContext,
):

    # Finding how many lines are covered by the requirements in the file.
    # Quick and dirty: https://stackoverflow.com/a/15273749/598057
    merged_ranges = []
    for pragma in source_file_traceability_info.pragmas:
        if pragma.begin_or_end != "BEGIN":
            continue
        begin, end = pragma.ng_source_line_begin, pragma.ng_source_line_end
        if merged_ranges and merged_ranges[-1][1] >= (begin - 1):
            merged_ranges[-1][1] = max(merged_ranges[-1][1], end)
        else:
            merged_ranges.append([begin, end])
    coverage = 0
    for merged_range in merged_ranges:
        coverage += merged_range[1] - merged_range[0]
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
        f"STRICT RANGE pragma should START and END with the same requirement(s): '{lhs_pragma_reqs_str}' != '{rhs_pragma_reqs_str}'.",
        """
# STRICTDOC RANGE BEGIN: REQ-001
Content...
# STRICTDOC RANGE END: REQ-001
        """.lstrip(),
        line=location["line"],
        col=location["col"],
        filename=location["filename"],
    )


def create_end_without_begin_error(location):
    return StrictDocSemanticError(
        "STRICTDOC RANGE: END pragma without preceding BEGIN pragma",
        "STRICT RANGE shall be opened with START pragma and ended with END pragma.",
        """
# STRICTDOC RANGE BEGIN: REQ-001
Content...
# STRICTDOC RANGE END: REQ-001
        """.lstrip(),
        line=location["line"],
        col=location["col"],
        filename=location["filename"],
    )


def range_start_pragma_processor(
    pragma: RangePragma, parse_context: ParseContext
):
    location = get_location(pragma)
    line = location["line"]
    pragma.ng_source_line_begin = line

    if pragma.begin_or_end == "BEGIN":
        parse_context.pragma_stack.append(pragma)
        parse_context.map_lines_to_pragmas[line] = pragma
        for req in pragma.reqs:
            pragmas = parse_context.map_reqs_to_pragmas.setdefault(req, [])
            pragmas.append(pragma)

    elif pragma.begin_or_end == "END":
        try:
            current_top_pragma: RangePragma = parse_context.pragma_stack.pop()
            if pragma.reqs != current_top_pragma.reqs:
                raise create_begin_end_range_reqs_mismatch_error(
                    location, current_top_pragma.reqs, pragma.reqs
                )
            current_top_pragma.ng_source_line_end = line
        except IndexError:
            raise create_end_without_begin_error(location)
    else:
        raise NotImplementedError


class SourceFileTraceabilityReader:
    SOURCE_FILE_MODELS = [SourceFileTraceabilityInfo, RangePragma]

    def __init__(self):
        self.meta_model = metamodel_from_str(
            SOURCE_FILE_GRAMMAR,
            classes=SourceFileTraceabilityReader.SOURCE_FILE_MODELS,
            use_regexp_group=True,
        )

    def read(self, input, file_path=None):
        # TODO: This might be possible to handle directly in the textx grammar.
        # AttributeError: 'str' object has no attribute '_tx_parser'
        file_size = len(input)
        if file_size == 0:
            return SourceFileTraceabilityInfo([])

        length = input.count("\n") + 1
        parse_context = ParseContext(length)

        parse_source_file_traceability_info_processor = partial(
            source_file_traceability_info_processor, parse_context=parse_context
        )
        parse_range_start_pragma_processor = partial(
            range_start_pragma_processor, parse_context=parse_context
        )

        obj_processors = {
            "SourceFileTraceabilityInfo": parse_source_file_traceability_info_processor,
            "RangePragma": parse_range_start_pragma_processor,
        }

        self.meta_model.register_obj_processors(obj_processors)

        try:
            source_file_traceability_info: SourceFileTraceabilityInfo = (
                self.meta_model.model_from_str(input, file_name=file_path)
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

        # parse_context.document_reference.set_document(source_file_traceability_info)

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        source_file_traceability_info._tx_parser = None
        source_file_traceability_info._tx_attrs = None
        source_file_traceability_info._tx_metamodel = None
        source_file_traceability_info._tx_peg_rule = None

        return source_file_traceability_info

    def read_from_file(self, file_path):
        with open(file_path, "r") as file:
            sdoc_content = file.read()
        try:
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc
        except NotImplementedError as exc:
            traceback.print_exc()
            exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())
            exit(1)
        except Exception as exc:
            print(
                "error: SourceFileTraceabilityReader: could not parse file: {}.\n{}: {}".format(
                    file_path, exc.__class__.__name__, exc
                )
            )
            # TODO: when --debug is provided
            # traceback.print_exc()
            exit(1)
