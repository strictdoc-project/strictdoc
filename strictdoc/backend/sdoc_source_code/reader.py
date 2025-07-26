"""
@relation(SDOC-SRS-142, scope=file)
"""

from functools import partial
from typing import Any, Dict, List, Optional, TypedDict, Union

from textx import get_location, metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.grammar import SOURCE_FILE_GRAMMAR
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.helpers.file_stats import SourceFileStats
from strictdoc.helpers.list import find_duplicates
from strictdoc.helpers.textx import drop_textx_meta


class TextXLocation(TypedDict):
    line: int
    col: int
    filename: str


def req_processor(req: Req) -> None:
    assert isinstance(req, Req), (
        f"Expected req to be Req, got: {req}, {type(req)}"
    )
    location = get_location(req)
    assert location
    req.ng_source_line = location["line"]
    req.ng_source_column = location["col"]


def source_file_traceability_info_processor(
    source_file_traceability_info: SourceFileTraceabilityInfo,
    parse_context: ParseContext,
) -> None:
    if len(parse_context.marker_stack) > 0:
        raise create_unmatch_range_error(
            parse_context.marker_stack,
        )
    source_file_traceability_info.markers = parse_context.markers
    source_file_traceability_info.file_stats = parse_context.file_stats


def create_begin_end_range_reqs_mismatch_error(
    location: Dict[str, Any],
    lhs_marker_reqs: List[str],
    rhs_marker_reqs: List[str],
) -> StrictDocSemanticError:
    lhs_marker_reqs_str = ", ".join(lhs_marker_reqs)
    rhs_marker_reqs_str = ", ".join(rhs_marker_reqs)

    return StrictDocSemanticError(
        "STRICTDOC RANGE: BEGIN and END requirements mismatch",
        (
            "STRICT RANGE marker should START and END "
            "with the same requirement(s): "
            f"'{lhs_marker_reqs_str}' != '{rhs_marker_reqs_str}'."
        ),
        # @sdoc[nosdoc]  # noqa: ERA001
        """
# [REQ-001]
Content...
# [/REQ-001]
        """.lstrip(),
        # @sdoc[/nosdoc]  # noqa: ERA001
        line=location["line"],
        col=location["col"],
        filename=location["filename"],
    )


def create_end_without_begin_error(
    location: Dict[str, Any],
) -> StrictDocSemanticError:
    return StrictDocSemanticError(
        "STRICTDOC RANGE: END marker without preceding BEGIN marker",
        (
            "STRICT RANGE shall be opened with "
            "START marker and ended with END marker."
        ),
        # @sdoc[nosdoc]  # noqa: ERA001
        """
# [REQ-001]
Content...
# [/REQ-001]
        """.lstrip(),
        # @sdoc[/nosdoc]  # noqa: ERA001
        line=location["line"],
        col=location["col"],
        filename=location["filename"],
    )


def create_unmatch_range_error(
    unmatched_ranges: List[RangeMarker],
) -> StrictDocSemanticError:
    assert isinstance(unmatched_ranges, list)
    assert len(unmatched_ranges) > 0
    range_locations: List[TextXLocation] = []
    for unmatched_range in unmatched_ranges:
        location = get_location(unmatched_range)
        range_locations.append(location)
    first_location = range_locations[0]
    hint: Optional[str] = None
    if len(unmatched_ranges) > 1:
        range_lines = list(map(lambda loc: loc["line"], range_locations[1:]))
        hint = f"The @sdoc keywords are also unmatched on lines: {range_lines}."

    return StrictDocSemanticError(
        "Unmatched @sdoc keyword found in source file.",
        hint=hint,
        # @sdoc[nosdoc]
        example=(
            "Each @sdoc keyword must be matched with a closing keyword. "
            "Example:\n"
            "@sdoc[REQ-001]\n"
            "...\n"
            "@sdoc[/REQ-001]"
        ),
        # @sdoc[/nosdoc]
        line=first_location["line"],
        col=first_location["col"],
        filename=first_location["filename"],
    )


def validate_marker_uids(
    marker: Union[FunctionRangeMarker, LineMarker, RangeMarker],
    parse_context: ParseContext,
) -> None:
    possible_duplicates = find_duplicates(marker.reqs)
    if len(possible_duplicates) > 0:
        location = get_location(marker)

        raise ValueError(
            "@relation marker contains duplicate node UIDs: "
            f"{possible_duplicates}. Location: {parse_context.filename}:{location['line']}."
        )


def range_marker_processor(
    marker: RangeMarker, parse_context: ParseContext
) -> None:
    validate_marker_uids(marker, parse_context)

    location = get_location(marker)
    line = location["line"]

    current_top_marker: RangeMarker
    if marker.ng_is_nodoc:
        if marker.is_begin():
            parse_context.marker_stack.append(marker)
        elif marker.is_end():
            try:
                current_top_marker = parse_context.marker_stack.pop()
                if (
                    not current_top_marker.ng_is_nodoc
                    or current_top_marker.is_end()
                ):
                    raise create_begin_end_range_reqs_mismatch_error(
                        location, current_top_marker.reqs, marker.reqs
                    )
            except IndexError:
                raise create_end_without_begin_error(location) from None
        return

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "nosdoc" block, so we ignore it.
        return

    parse_context.markers.append(marker)
    marker.ng_source_line_begin = line

    if marker.is_begin():
        marker.ng_range_line_begin = line
        parse_context.marker_stack.append(marker)
        for req in marker.reqs:
            markers = parse_context.map_reqs_to_markers.setdefault(req, [])
            markers.append(marker)

    elif marker.is_end():
        try:
            current_top_marker = parse_context.marker_stack.pop()
            if marker.reqs != current_top_marker.reqs:
                raise create_begin_end_range_reqs_mismatch_error(
                    location, current_top_marker.reqs, marker.reqs
                )
            current_top_marker.ng_range_line_end = line

            marker.ng_range_line_begin = current_top_marker.ng_range_line_begin
            marker.ng_range_line_end = line

        except IndexError:
            raise create_end_without_begin_error(location) from None
    else:
        raise NotImplementedError


def line_marker_processor(
    line_marker: LineMarker, parse_context: ParseContext
) -> None:
    validate_marker_uids(line_marker, parse_context)

    location = get_location(line_marker)
    line = location["line"]

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "nosdoc" block, so we ignore it.
        return

    parse_context.markers.append(line_marker)
    line_marker.ng_source_line_begin = line
    line_marker.ng_range_line_begin = line
    line_marker.ng_range_line_end = line

    for req in line_marker.reqs:
        markers = parse_context.map_reqs_to_markers.setdefault(req, [])
        markers.append(line_marker)


def function_range_marker_processor(
    function_range_marker: FunctionRangeMarker, parse_context: ParseContext
) -> None:
    validate_marker_uids(function_range_marker, parse_context)

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "nosdoc" block, so we ignore it.
        return

    parse_context.markers.append(function_range_marker)
    function_range_marker.ng_source_line_begin = 1
    function_range_marker.ng_range_line_begin = 1
    function_range_marker.ng_range_line_end = (
        parse_context.file_stats.lines_total
    )

    for req in function_range_marker.reqs:
        markers = parse_context.map_reqs_to_markers.setdefault(req, [])
        markers.append(function_range_marker)


class SourceFileTraceabilityReader:
    SOURCE_FILE_MODELS = [
        FunctionRangeMarker,
        LineMarker,
        Req,
        SourceFileTraceabilityInfo,
        RangeMarker,
    ]

    def __init__(self) -> None:
        self.meta_model = metamodel_from_str(
            SOURCE_FILE_GRAMMAR,
            classes=SourceFileTraceabilityReader.SOURCE_FILE_MODELS,
            use_regexp_group=True,
        )

    def read(
        self, input_string: str, file_path: Optional[str] = None
    ) -> SourceFileTraceabilityInfo:
        # TODO: This might be possible to handle directly in the textx grammar.
        # AttributeError: 'str' object has no attribute '_tx_parser'.
        file_size = len(input_string)
        if file_size == 0:
            return SourceFileTraceabilityInfo([])

        file_stats = SourceFileStats.create(input_string)
        parse_context = ParseContext(file_path, file_stats)

        parse_source_traceability_processor = partial(
            source_file_traceability_info_processor, parse_context=parse_context
        )
        parse_req_processor = partial(req_processor)
        parse_range_marker_processor = partial(
            range_marker_processor, parse_context=parse_context
        )
        parse_line_marker_processor = partial(
            line_marker_processor, parse_context=parse_context
        )
        parse_function_range_marker_processor = partial(
            function_range_marker_processor, parse_context=parse_context
        )

        obj_processors = {
            "FunctionRangeMarker": parse_function_range_marker_processor,
            "LineMarker": parse_line_marker_processor,
            "RangeMarker": parse_range_marker_processor,
            "Req": parse_req_processor,
            "SourceFileTraceabilityInfo": parse_source_traceability_processor,
        }

        self.meta_model.register_obj_processors(obj_processors)

        source_file_traceability_info: SourceFileTraceabilityInfo = (
            self.meta_model.model_from_str(input_string, file_name=file_path)
        )
        source_file_traceability_info.ng_map_reqs_to_markers = (
            parse_context.map_reqs_to_markers
        )

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(source_file_traceability_info)
        return source_file_traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        with open(file_path, encoding="utf-8") as file:
            sdoc_content = file.read()
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc
