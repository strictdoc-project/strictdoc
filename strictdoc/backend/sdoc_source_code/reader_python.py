# mypy: disable-error-code="no-redef,no-untyped-call,no-untyped-def,type-arg,var-annotated"
import re
import sys
import traceback
from typing import Generator
from typing import List, Optional, Union

import tree_sitter_python
from tree_sitter import Language, Parser, Tree, Node

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    LineMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.string import get_lines_count

REGEX_REQ = r"[A-Za-z][A-Za-z0-9\\-]+"
REGEX_RANGE = rf"@sdoc\[(/?)({REGEX_REQ}(?:, {REGEX_REQ})*)\]"
REGEX_LINE = (
    rf"@sdoc\((/?)({REGEX_REQ}(?:, {REGEX_REQ})*)\)"
)


class ParseContext:
    def __init__(self, filename: str, lines_total):
        self.filename: str = filename
        self.lines_total = lines_total
        self.markers = []
        self.marker_stack: List[RangeMarker] = []
        self.map_lines_to_markers = {}
        self.map_reqs_to_markers = {}


def source_file_traceability_info_processor(
    source_file_traceability_info: SourceFileTraceabilityInfo,
    parse_context: ParseContext,
):
    if len(parse_context.marker_stack) > 0:
        raise create_unmatch_range_error(
            parse_context.marker_stack, parse_context.filename
        )
    source_file_traceability_info.markers = parse_context.markers
    # Finding how many lines are covered by the requirements in the file.
    # Quick and dirty: https://stackoverflow.com/a/15273749/598057
    merged_ranges = []
    marker: Union[LineMarker, RangeMarker, ForwardRangeMarker]
    for marker in source_file_traceability_info.markers:
        # At this point, we don't have any ForwardRangeMarkers because they
        # come from Requirements, not from source code.
        assert isinstance(marker, (RangeMarker, LineMarker)), marker
        if marker.ng_is_nodoc:
            continue
        if not marker.is_begin():
            continue
        begin, end = (
            assert_cast(marker.ng_range_line_begin, int),
            assert_cast(marker.ng_range_line_end, int),
        )
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
    filename, line, col, lhs_marker_reqs, rhs_marker_reqs
):
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
        line=line,
        col=col,
        filename=filename,
    )


def create_end_without_begin_error(filename, line, col):
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
        line=line,
        col=col,
        filename=filename,
    )


def create_unmatch_range_error(unmatched_ranges: List[Union[RangeMarker, LineMarker]], filename):
    assert isinstance(unmatched_ranges, list)
    assert len(unmatched_ranges) > 0
    range_locations: List = []
    for unmatched_range_ in unmatched_ranges:
        range_locations.append(
            (unmatched_range_.ng_source_line_begin, unmatched_range_.ng_source_column_begin)
        )
    first_location = range_locations[0]
    hint: Optional[str] = None
    if len(unmatched_ranges) > 1:
        range_lines = range_locations[1:]
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
        line=first_location[0],
        col=first_location[1],
        filename=filename,
    )


def range_marker_processor(marker: RangeMarker, parse_context: ParseContext):
    if marker.ng_is_nodoc:
        if marker.is_begin():
            parse_context.marker_stack.append(marker)
        elif marker.is_end():
            try:
                current_top_marker: RangeMarker = (
                    parse_context.marker_stack.pop()
                )
                if (
                    not current_top_marker.ng_is_nodoc
                    or current_top_marker.is_end()
                ):
                    raise create_begin_end_range_reqs_mismatch_error(
                        "FIXME", -1, -1, current_top_marker.reqs, marker.reqs
                    )
            except IndexError:
                raise create_end_without_begin_error("FIXME", -1, -1) from None
        return

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "nosdoc" block, so we ignore it.
        return

    parse_context.markers.append(marker)

    parse_context.map_lines_to_markers[marker.ng_source_line_begin] = marker

    if marker.is_begin():
        marker.ng_range_line_begin = marker.ng_source_line_begin
        parse_context.marker_stack.append(marker)
        parse_context.map_lines_to_markers[marker.ng_source_line_begin] = marker
        for req in marker.reqs:
            markers = parse_context.map_reqs_to_markers.setdefault(req, [])
            markers.append(marker)

    elif marker.is_end():
        try:
            current_top_marker: RangeMarker = parse_context.marker_stack.pop()
            if marker.reqs != current_top_marker.reqs:
                raise create_begin_end_range_reqs_mismatch_error(
                    "FIXME",
                    marker.ng_source_line_begin,
                    -1,
                    current_top_marker.reqs,
                    marker.reqs,
                )

            current_top_marker.ng_range_line_end = marker.ng_source_line_begin

            marker.ng_range_line_end = marker.ng_range_line_begin
            marker.ng_range_line_begin = current_top_marker.ng_range_line_begin

        except IndexError:
            raise create_end_without_begin_error("FIXME", 1, 1) from None
    else:
        raise NotImplementedError


def line_marker_processor(line_marker: LineMarker, parse_context: ParseContext):
    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "nosdoc" block, so we ignore it.
        return

    parse_context.markers.append(line_marker)

    parse_context.map_lines_to_markers[line_marker.ng_source_line_begin] = line_marker

    for req in line_marker.reqs:
        markers = parse_context.map_reqs_to_markers.setdefault(req, [])
        markers.append(line_marker)


def sdoc_tree_sitter_dump_node(node):
    print("Byte range: ", node.byte_range)
    print("Range: ", node.range)
    print("Type: ", node.type)


class SourceFileTraceabilityReader_Python:
    def __init__(self):
        pass

    def read(self, input_buffer: bytes, file_path=None):
        assert isinstance(input_buffer, bytes)

        file_size = len(input_buffer)

        traceability_info = SourceFileTraceabilityInfo([])

        if file_size == 0:
            return traceability_info

        length = get_lines_count(input_buffer)
        parse_context = ParseContext(file_path, length)

        language_arg = tree_sitter_python.language()
        PY_LANGUAGE = Language(language_arg)

        parser = Parser(PY_LANGUAGE)

        tree = parser.parse(input_buffer)

        def traverse_tree(tree: Tree) -> Generator[Node, None, None]:
            cursor = tree.walk()

            visited_children = False
            while True:
                if not visited_children:
                    yield cursor.node, cursor.depth
                    if not cursor.goto_first_child():
                        visited_children = True
                elif cursor.goto_next_sibling():
                    visited_children = False
                elif not cursor.goto_parent():
                    break

        functions_stack: List[Function] = []

        nodes = traverse_tree(tree)
        map_function_to_node = {}
        for node_, node_depth_ in nodes:
            if node_.type == "module":
                function = Function(parent=None, name="module", parts=[])
                functions_stack.append(function)
                map_function_to_node[function] = node_
            elif node_.type == "function_definition":
                function_name = None
                for child in node_.children:
                    if child.type == "identifier":
                        function_name = child.text.decode("utf-8")
                        break

                cursor = node_
                while cursor := cursor.parent:
                    if cursor == map_function_to_node[functions_stack[-1]]:
                        break
                    if cursor.type == "function_definition":
                        functions_stack.pop()
                        assert len(functions_stack) > 0
                else:
                    # This is counterintuitive:
                    # The top-level functions don't have the top-level module set
                    # as their parent, so in this branch, we simply clear the whole
                    # function stack, leaving the top module only.
                    functions_stack = functions_stack[:1]

                new_function = Function(
                    parent=None, name=function_name, parts=[]
                )
                map_function_to_node[new_function] = node_

                parent_function = functions_stack[-1]

                parent_function.parts.append(new_function)
                functions_stack.append(new_function)
                traceability_info.functions.append(new_function)
            elif node_.type == "comment":
                # @sdoc[REQ-001]
                node_text_string = node_.text.decode("utf8")

                match_line = None
                match_range = re.search(REGEX_RANGE, node_text_string)
                if match_range is None:
                    match_line = re.search(REGEX_LINE, node_text_string)

                match = match_range if match_range is not None else match_line
                if match is None:
                    continue

                start_or_end = match.group(1) != "/"
                req_list = match.group(2)

                first_requirement_index = match.start(2)
                requirements = []
                for req_match in re.finditer(REGEX_REQ, req_list):
                    req_item = req_match.group(0)  # Matched REQ-XXX item
                    # Calculate actual position relative to the original string
                    start_index = (
                        req_match.start()
                    )  # Offset by where group 1 starts

                    requirement = Req(None, req_item)
                    requirement.ng_source_line = node_.range.start_point[0]
                    requirement.ng_source_column = (
                        first_requirement_index + start_index
                    )
                    requirements.append(requirement)

                if match_range is not None:
                    range_marker = RangeMarker(
                        None, "[" if start_or_end else "[/", requirements
                    )
                    range_marker.ng_source_line_begin = (
                        node_.range.start_point[0] + 1
                    )
                    range_marker.ng_range_line_begin = (
                        node_.range.start_point[0] + 1
                    )
                    range_marker.ng_source_column_begin = (
                        first_requirement_index + 1
                    )
                    range_marker_processor(range_marker, parse_context)
                    traceability_info.markers.append(range_marker)

                elif match_line is not None:
                    line_marker = LineMarker(None, requirements)
                    line_marker.ng_source_line_begin = (
                        node_.range.start_point[0] + 1
                    )
                    line_marker.ng_range_line_begin = (
                        node_.range.start_point[0] + 1
                    )
                    line_marker.ng_range_line_end = (
                        node_.range.start_point[0] + 1
                    )

                    line_marker_processor(line_marker, parse_context)
                else:
                    raise AssertionError("Must not reach here.")
            else:
                pass

        assert functions_stack[0].name == "module"

        traceability_info.parts = functions_stack[0].parts
        source_file_traceability_info_processor(
            traceability_info, parse_context
        )

        return traceability_info

    def read_from_file(self, file_path):
        try:
            with open(file_path, "rb") as file:
                sdoc_content = file.read()
                sdoc = self.read(sdoc_content, file_path=file_path)
                return sdoc
        except NotImplementedError:
            traceback.print_exc()
            sys.exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(  # noqa: T201
                f"error: SourceFileTraceabilityReader_Python: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided
            # traceback.print_exc()  # noqa: ERA001
            sys.exit(1)
