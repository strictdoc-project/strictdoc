"""
@relation(SDOC-SRS-33, scope=file)
"""

from typing import List, Optional, Tuple, Union

from textx import get_location

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.list import find_duplicates


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


def _handle_skip_marker(
    marker: Union[RangeMarker, FunctionRangeMarker, LineMarker],
    parse_context: ParseContext,
) -> None:
    assert marker.ng_is_nodoc, marker
    assert marker.ng_source_line_begin is not None, marker
    assert marker.ng_source_column_begin is not None, marker

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
                    parse_context.filename,
                    assert_cast(current_top_marker.ng_source_line_begin, int),
                    assert_cast(current_top_marker.ng_source_column_begin, int),
                    current_top_marker.reqs,
                    marker.reqs,
                )
        except IndexError:
            raise create_end_without_begin_error(
                parse_context.filename,
                marker.ng_source_line_begin,
                marker.ng_source_column_begin,
            ) from None


def source_file_traceability_info_processor(
    source_file_traceability_info: SourceFileTraceabilityInfo,
    parse_context: ParseContext,
) -> None:
    if len(parse_context.marker_stack) > 0:
        if any(
            not marker_.ng_is_nodoc for marker_ in parse_context.marker_stack
        ):
            raise create_unmatch_range_error(
                parse_context.marker_stack, filename=parse_context.filename
            )
    source_file_traceability_info.markers = parse_context.markers
    source_file_traceability_info.file_stats = parse_context.file_stats
    source_file_traceability_info.ng_map_reqs_to_markers = (
        parse_context.map_reqs_to_markers
    )


def create_begin_end_range_reqs_mismatch_error(
    filename: str,
    line: int,
    col: int,
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
        # @relation(skip, scope=range_start)  # noqa: ERA001
        """
# [REQ-001]
Content...
# [/REQ-001]
        """.lstrip(),
        # @relation(skip, scope=range_end)  # noqa: ERA001
        line=line,
        col=col,
        filename=filename,
    )


def create_end_without_begin_error(
    filename: str, line: int, col: int
) -> StrictDocSemanticError:
    return StrictDocSemanticError(
        "STRICTDOC RANGE: END marker without preceding BEGIN marker",
        (
            "STRICT RANGE shall be opened with "
            "START marker and ended with END marker."
        ),
        # @relation(skip, scope=range_start)  # noqa: ERA001
        """
# [REQ-001]
Content...
# [/REQ-001]
        """.lstrip(),
        # @relation(skip, scope=range_end)  # noqa: ERA001
        line=line,
        col=col,
        filename=filename,
    )


def create_unmatch_range_error(
    unmatched_ranges: List[Union[RangeMarker, FunctionRangeMarker, LineMarker]],
    filename: Optional[str],
) -> StrictDocSemanticError:
    assert isinstance(unmatched_ranges, list)
    assert len(unmatched_ranges) > 0
    range_locations: List[Tuple[int, int]] = []
    for unmatched_range_ in unmatched_ranges:
        assert unmatched_range_.ng_source_line_begin is not None
        assert unmatched_range_.ng_source_column_begin is not None
        range_locations.append(
            (
                unmatched_range_.ng_source_line_begin,
                unmatched_range_.ng_source_column_begin,
            )
        )
    first_location = range_locations[0]
    hint: Optional[str] = None
    if len(unmatched_ranges) > 1:
        range_lines = range_locations[1:]
        hint = f"The @relation keywords are also unmatched on lines: {range_lines}."

    return StrictDocSemanticError(
        "Unmatched @relation keyword found in source file.",
        hint=hint,
        # @relation(skip, scope=range_start)
        example=(
            "Each @relation keyword must be matched with a closing keyword. "
            "Example:\n"
            "@relation(REQ-001, scope=range_start)\n"
            "...\n"
            "@relation(REQ-001, scope=range_end)"
        ),
        # @relation(skip, scope=range_end)
        line=first_location[0],
        col=first_location[1],
        filename=filename,
    )


def function_range_marker_processor(
    marker: FunctionRangeMarker, parse_context: ParseContext
) -> None:
    if marker.ng_is_nodoc:
        _handle_skip_marker(marker, parse_context)
        return

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "@relation(skip...)" block, so we ignore it.
        return

    parse_context.markers.append(marker)

    assert marker.ng_source_line_begin is not None
    for req in marker.reqs:
        markers = parse_context.map_reqs_to_markers.setdefault(req, [])
        markers.append(marker)


def range_marker_processor(
    marker: RangeMarker, parse_context: ParseContext
) -> None:
    if marker.ng_is_nodoc:
        _handle_skip_marker(marker, parse_context)
        return

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "@relation(skip...)" block, so we ignore it.
        return

    parse_context.markers.append(marker)

    assert marker.ng_source_line_begin is not None

    if marker.is_begin():
        marker.ng_range_line_begin = marker.ng_source_line_begin
        parse_context.marker_stack.append(marker)
        assert marker.ng_source_line_begin is not None
        for req in marker.reqs:
            markers = parse_context.map_reqs_to_markers.setdefault(req, [])
            markers.append(marker)

    elif marker.is_end():
        try:
            current_top_marker = parse_context.marker_stack.pop()
            if marker.reqs != current_top_marker.reqs:
                assert marker.ng_source_line_begin is not None
                raise create_begin_end_range_reqs_mismatch_error(
                    parse_context.filename,
                    assert_cast(marker.ng_source_line_begin, int),
                    assert_cast(marker.ng_source_column_begin, int),
                    current_top_marker.reqs,
                    marker.reqs,
                )

            current_top_marker.ng_range_line_end = marker.ng_source_line_begin

            marker.ng_range_line_end = marker.ng_range_line_begin
            marker.ng_range_line_begin = current_top_marker.ng_range_line_begin

        except IndexError:
            raise create_end_without_begin_error(
                parse_context.filename,
                assert_cast(marker.ng_source_line_begin, int),
                assert_cast(marker.ng_source_column_begin, int),
            ) from None
    else:
        raise NotImplementedError


def line_marker_processor(
    line_marker: LineMarker, parse_context: ParseContext
) -> None:
    validate_marker_uids(line_marker, parse_context)

    # If the object is coming from textX, obtain information from textX parsing
    # information.
    line: int
    if line_marker.ng_source_line_begin is None:
        location = get_location(line_marker)
        line = location["line"]
        line_marker.ng_source_line_begin = line
        line_marker.ng_range_line_begin = line
        line_marker.ng_range_line_end = line + 1
    else:
        line = line_marker.ng_source_line_begin

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "@relation(skip...)" block, so we ignore it.
        return

    has_previous_markers = len(parse_context.markers) > 0
    is_consecutive = (
        has_previous_markers
        and parse_context.markers[-1].ng_range_line_end == line
    )
    if is_consecutive:
        raise StrictDocSemanticError(
            "Consecutive LineMarkers are not allowed",
            hint=None,
            example=None,
            line=line,
            filename=parse_context.filename,
        )

    is_at_eof = line == parse_context.file_stats.lines_total
    if is_at_eof:
        raise StrictDocSemanticError(
            "LineMarker cannot be followed by EOF",
            hint=None,
            example=None,
            line=line,
            filename=parse_context.filename,
        )

    parse_context.markers.append(line_marker)
    for req in line_marker.reqs:
        markers = parse_context.map_reqs_to_markers.setdefault(req, [])
        markers.append(line_marker)
