"""
@relation(SDOC-SRS-142, SDOC-SRS-147, scope=file)
"""

from itertools import islice
from typing import Any, List, Optional, Sequence, Tuple

import tree_sitter_python
from tree_sitter import Language, Node, Parser

from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    RelationMarkerType,
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.models.source_location import ByteRange
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    function_range_marker_processor,
    line_marker_processor,
    range_marker_processor,
    source_file_traceability_info_processor,
)
from strictdoc.backend.sdoc_source_code.tree_sitter_helpers import traverse_tree
from strictdoc.helpers.file_stats import SourceFileStats
from strictdoc.helpers.file_system import file_open_read_bytes


class SourceFileTraceabilityReader_Python:
    def read(
        self, input_buffer: bytes, file_path: Optional[str] = None
    ) -> SourceFileTraceabilityInfo:
        assert isinstance(input_buffer, bytes)

        file_size = len(input_buffer)

        traceability_info = SourceFileTraceabilityInfo([])

        if file_size == 0:
            return traceability_info

        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)

        # Works since Python 3.9 but we also lint this with mypy from Python 3.8.
        language_arg = tree_sitter_python.language()
        py_language = Language(  # type: ignore[call-arg, unused-ignore]
            language_arg
        )
        parser = Parser(py_language)  # type: ignore[call-arg, unused-ignore]

        tree = parser.parse(input_buffer)

        functions_stack: List[Function] = []

        nodes = traverse_tree(tree)
        map_function_to_node = {}

        visited_comments = set()
        for node_ in nodes:
            if node_.type == "module":
                function = Function(
                    parent=traceability_info,
                    name="module",
                    display_name="module",
                    line_begin=node_.start_point[0] + 1,
                    line_end=node_.end_point[0] + 1,
                    code_byte_range=ByteRange.create_from_ts_node(node_),
                    child_functions=[],
                    markers=[],
                    attributes=set(),
                )
                functions_stack.append(function)
                map_function_to_node[function] = node_
                if len(node_.children) > 0:
                    # Look for the docstring within the first 30 children (arbitrary chosen limit)
                    # so that we dont miss it if the file starts with comments (#!, encoding marker, etc...).
                    first_match = next(
                        (
                            child
                            for child in islice(node_.children, 30)
                            if child.type == "expression_statement"
                            and len(child.children) > 0
                            and child.children[0].type == "string"
                        ),
                        None,
                    )

                    if first_match is not None:
                        block_comment = first_match.children[0]

                        # String contains of three parts:
                        # (string_start string_content string_end)
                        string_content = block_comment.children[1]
                        assert string_content.text is not None

                        block_comment_text = string_content.text.decode("utf-8")
                        source_node = MarkerParser.parse(
                            input_string=block_comment_text,
                            line_start=node_.start_point[0] + 1,
                            # It is important that +1 is not present here because
                            # currently StrictDoc does not display the last empty line (\n is 10).
                            line_end=node_.end_point[0]
                            if input_buffer[-1] == 10
                            else node_.end_point[0] + 1,
                            comment_line_start=string_content.start_point[0]
                            + 1,
                            comment_byte_range=ByteRange.create_from_ts_node(
                                string_content
                            ),
                        )
                        for marker_ in source_node.markers:
                            if isinstance(marker_, FunctionRangeMarker) and (
                                function_range_marker_ := marker_
                            ):
                                function_range_marker_processor(
                                    function_range_marker_, parse_context
                                )
                                traceability_info.markers.append(
                                    function_range_marker_
                                )

            elif node_.type in ("class_definition", "function_definition"):
                function_name: str = ""
                function_block: Optional[Node] = None

                for child_ in node_.children:
                    if child_.type == "identifier":
                        if child_.text is not None:
                            function_name = child_.text.decode("utf-8")
                    if child_.type == "block":
                        function_block = child_

                assert function_name is not None, "Function name"

                parent_names = self.get_node_ns(node_)
                if parent_names:
                    function_name = f"{'.'.join(parent_names)}.{function_name}"

                function_markers: List[RelationMarkerType] = []
                block_comment = None
                if (
                    function_block is not None
                    and len(function_block.children) > 0
                    and function_block.children[0].type
                    == "expression_statement"
                ):
                    if len(function_block.children[0].children) > 0:
                        if (
                            function_block.children[0].children[0].type
                            == "string"
                        ):
                            block_comment = function_block.children[0].children[
                                0
                            ]
                            # String contains of three parts:
                            # (string_start string_content string_end)
                            string_content = block_comment.children[1]
                            assert string_content.text is not None

                            block_comment_text = string_content.text.decode(
                                "utf-8"
                            )
                            source_node = MarkerParser.parse(
                                input_string=block_comment_text,
                                line_start=node_.start_point[0] + 1,
                                line_end=node_.end_point[0] + 1,
                                comment_line_start=string_content.start_point[0]
                                + 1,
                                comment_byte_range=ByteRange.create_from_ts_node(
                                    string_content
                                ),
                                entity_name=function_name,
                            )
                            for marker_ in source_node.markers:
                                if isinstance(marker_, FunctionRangeMarker):
                                    function_range_marker_processor(
                                        marker_, parse_context
                                    )
                                    traceability_info.markers.append(marker_)
                                    function_markers.append(marker_)

                # FIXME: This look more complex than needed but can't make mypy happy.
                cursor_: Optional[Node] = node_
                while cursor_ is not None and (cursor_ := cursor_.parent):
                    if cursor_ == map_function_to_node[functions_stack[-1]]:
                        break
                    if cursor_.type == "function_definition":
                        functions_stack.pop()
                        assert len(functions_stack) > 0
                else:
                    # This is counterintuitive:
                    # The top-level functions don't have the top-level module set
                    # as their parent, so in this branch, we simply clear the whole
                    # function stack, leaving the top module only.
                    functions_stack = functions_stack[:1]

                new_function = Function(
                    parent=traceability_info,
                    name=function_name,
                    display_name=function_name,
                    line_begin=node_.range.start_point[0] + 1,
                    line_end=node_.range.end_point[0] + 1,
                    code_byte_range=ByteRange.create_from_ts_node(node_),
                    child_functions=[],
                    # Python functions do not need to track markers.
                    markers=[],
                    attributes=set(),
                )
                map_function_to_node[new_function] = node_

                parent_function = functions_stack[-1]

                parent_function.child_functions.append(new_function)
                functions_stack.append(new_function)
                traceability_info.functions.append(new_function)

                traceability_info.ng_map_names_to_markers[function_name] = (
                    function_markers
                )
            elif node_.type == "comment":
                if node_ in visited_comments:
                    continue

                assert node_.parent is not None
                assert node_.text is not None, (
                    f"Comment without a text: {node_}"
                )

                if not SourceFileTraceabilityReader_Python.is_comment_alone_on_line(
                    node_
                ):
                    continue

                merged_comments, last_idx = (
                    SourceFileTraceabilityReader_Python.collect_consecutive_comments(
                        node_
                    )
                )

                for j in range(node_.parent.children.index(node_), last_idx):
                    visited_comments.add(node_.parent.children[j])

                last_comment = node_.parent.children[last_idx - 1]

                source_node = MarkerParser.parse(
                    input_string=merged_comments,
                    line_start=node_.start_point[0] + 1,
                    line_end=last_comment.end_point[0] + 1,
                    comment_line_start=node_.start_point[0] + 1,
                    comment_byte_range=ByteRange(
                        node_.start_byte, last_comment.end_byte
                    ),
                    entity_name=None,
                )
                for marker_ in source_node.markers:
                    if isinstance(marker_, RangeMarker) and (
                        range_marker := marker_
                    ):
                        range_marker_processor(range_marker, parse_context)
                    elif isinstance(marker_, LineMarker) and (
                        line_marker := marker_
                    ):
                        line_marker_processor(line_marker, parse_context)
                    else:
                        pass
            else:
                pass

        assert (
            functions_stack[0].name == "module"
            or functions_stack[0].name == "translation_unit"
        )

        source_file_traceability_info_processor(
            traceability_info, parse_context
        )

        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        with file_open_read_bytes(file_path) as file:
            sdoc_content = file.read()
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc

    @staticmethod
    def get_node_ns(node: Node) -> Sequence[str]:
        """
        Walk up from node to find enclosing class and function names.

        Handles nested functions, methods, and classes.
        """
        parent_scopes: List[str] = []
        cursor: Optional[Node] = node

        while cursor is not None:
            if cursor.type in ("class_definition", "function_definition"):
                # Look for the identifier child (i.e., the name).
                name_node = next(
                    (
                        child
                        for child in cursor.children
                        if child.type == "identifier"
                    ),
                    None,
                )
                if name_node and name_node.text:
                    parent_scopes.insert(0, name_node.text.decode("utf-8"))
            cursor = cursor.parent

        # The array now contains the "fully qualified" node name,
        # we want to return the namespace, so don't return the last part.
        return parent_scopes[:-1]

    @staticmethod
    def collect_consecutive_comments(comment_node: Any) -> Tuple[str, int]:
        parent = comment_node.parent

        siblings = parent.children
        idx = siblings.index(comment_node)

        merged_texts = []

        last_node = None

        while idx < len(siblings) and siblings[idx].type == "comment":
            n = siblings[idx]
            assert n.text is not None
            text = n.text.decode("utf8")

            if last_node is not None:
                # Tree-sitter line numbers are 0-based
                last_end_line = last_node.end_point[0]
                curr_start_line = n.start_point[0]

                # Stop merging if there is an empty line between comments
                if curr_start_line > last_end_line + 1:
                    break

            merged_texts.append(text)
            last_node = n
            idx += 1

        return "\n".join(merged_texts), idx

    @staticmethod
    def is_comment_alone_on_line(node: Any) -> bool:
        """
        Return True if the comment node is the only thing on its line (ignoring whitespace).
        """

        if node.type != "comment":
            return False

        parent = node.parent
        assert parent is not None

        comment_line = node.start_point[0]

        for sibling in parent.children:
            if sibling is node:
                continue
            start_line = sibling.start_point[0]
            end_line = sibling.end_point[0]

            # If sibling shares the same line as comment
            if start_line <= comment_line <= end_line:
                # If it's not a comment (code, punctuation, etc.)
                if sibling.type != "comment":
                    return False

        return True
