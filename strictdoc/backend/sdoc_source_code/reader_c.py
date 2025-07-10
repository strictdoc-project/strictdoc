"""
@relation(SDOC-SRS-142, scope=file)
"""

import sys
import traceback
from typing import List, Optional, Sequence

import tree_sitter_cpp
from tree_sitter import Language, Node, Parser

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
    RangeMarkerType,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    function_range_marker_processor,
    line_marker_processor,
    range_marker_processor,
    source_file_traceability_info_processor,
)
from strictdoc.backend.sdoc_source_code.tree_sitter_helpers import (
    traverse_tree,
    ts_find_child_node_by_type,
    ts_find_child_nodes_by_type,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_stats import SourceFileStats


class SourceFileTraceabilityReader_C:
    def __init__(self, parse_nodes: bool = False) -> None:
        self.parse_nodes: bool = parse_nodes

    def read(
        self,
        input_buffer: bytes,
        file_path: str,
    ) -> SourceFileTraceabilityInfo:
        assert isinstance(input_buffer, bytes)

        file_size = len(input_buffer)

        traceability_info = SourceFileTraceabilityInfo([])

        if file_size == 0:
            return traceability_info

        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)

        # Works since Python 3.9 but we also lint this with mypy from Python 3.8.
        language_arg = tree_sitter_cpp.language()
        py_language = Language(  # type: ignore[call-arg, unused-ignore]
            language_arg
        )
        parser = Parser(py_language)  # type: ignore[call-arg, unused-ignore]

        tree = parser.parse(input_buffer)

        nodes = traverse_tree(tree)
        for node_ in nodes:
            function_name: str
            function_markers: List[FunctionRangeMarker]
            function_comment_node: Optional[Node]
            if node_.type == "translation_unit":
                if (
                    len(node_.children) > 0
                    and node_.children[0].type == "comment"
                    and (comment_node := node_.children[0])
                ):
                    if comment_node.text is not None:
                        comment_text = comment_node.text.decode("utf-8")
                        source_node = MarkerParser.parse(
                            comment_text,
                            node_.start_point[0] + 1,
                            # It is important that +1 is not present here because
                            # currently StrictDoc does not display the last empty line (\n is 10).
                            node_.end_point[0]
                            if input_buffer[-1] == 10
                            else node_.end_point[0] + 1,
                            node_.start_point[0] + 1,
                            parse_nodes=self.parse_nodes,
                        )
                        for marker_ in source_node.markers:
                            if not isinstance(marker_, FunctionRangeMarker):
                                continue
                            # At the top level, only accept the scope=file markers.
                            # Everything else will be handled by functions and classes.
                            if marker_.scope != RangeMarkerType.FILE:
                                continue
                            if isinstance(marker_, FunctionRangeMarker) and (
                                function_range_marker_ := marker_
                            ):
                                function_range_marker_processor(
                                    function_range_marker_, parse_context
                                )
                                traceability_info.markers.append(
                                    function_range_marker_
                                )

            elif node_.type in ("declaration", "field_declaration"):
                function_declarator_node = ts_find_child_node_by_type(
                    node_, "function_declarator"
                )

                # C++ reference declaration wrap the function declaration one time.
                if function_declarator_node is None:
                    # Example: "TrkVertex& operator-=(const TrkVertex& c);".
                    reference_declarator_node = ts_find_child_node_by_type(
                        node_, "reference_declarator"
                    )
                    if reference_declarator_node is None:
                        continue

                    function_declarator_node = ts_find_child_node_by_type(
                        reference_declarator_node, "function_declarator"
                    )
                    if function_declarator_node is None:
                        continue

                # For normal C functions the identifier is "identifier".
                # For C++, there are:
                # Class function declarations: bool CanSend(const CanFrame &frame);         # noqa: ERA001
                # Operators:                   TrkVertex& operator-=(const TrkVertex& c);   # noqa: ERA001
                # Destructors:                 ~TrkVertex();                                # noqa: ERA001
                function_identifier_node = self._get_function_name_node(
                    function_declarator_node,
                )
                if function_identifier_node is None:
                    continue

                if function_identifier_node.text is None:
                    continue

                assert function_identifier_node.text is not None, node_.text
                function_display_name = function_identifier_node.text.decode(
                    "utf8"
                )

                assert function_declarator_node.text is not None, node_.text
                function_name = function_declarator_node.text.decode("utf8")
                assert function_name is not None, node_.text

                parent_names = self.get_node_ns(node_)
                if len(parent_names) > 0:
                    function_name = (
                        f"{'::'.join(parent_names)}::{function_name}"
                    )
                    function_display_name = (
                        f"{'::'.join(parent_names)}::{function_display_name}"
                    )

                function_attributes = {FunctionAttribute.DECLARATION}
                for specifier_node_ in ts_find_child_nodes_by_type(
                    node_, "storage_class_specifier"
                ):
                    if specifier_node_.text == b"static":
                        function_attributes.add(FunctionAttribute.STATIC)

                function_markers = []
                function_comment_node = None
                if (
                    node_.prev_sibling is not None
                    and node_.prev_sibling.type == "comment"
                ):
                    function_comment_node = node_.prev_sibling
                    assert function_comment_node.text is not None, node_.text
                    function_comment_text = function_comment_node.text.decode(
                        "utf8"
                    )

                    function_last_line = node_.end_point[0] + 1

                    source_node = MarkerParser.parse(
                        function_comment_text,
                        function_comment_node.start_point[0] + 1,
                        function_last_line,
                        function_comment_node.start_point[0] + 1,
                        entity_name=function_display_name,
                        parse_nodes=self.parse_nodes,
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
                            function_markers.append(marker_)

                # The function range includes the top comment if it exists.
                new_function = Function(
                    parent=traceability_info,
                    name=function_name,
                    display_name=function_display_name,
                    line_begin=function_comment_node.start_point[0] + 1
                    if function_comment_node is not None
                    else node_.range.start_point[0] + 1,
                    line_end=node_.range.end_point[0] + 1,
                    child_functions=[],
                    markers=function_markers,
                    attributes=function_attributes,
                )
                traceability_info.functions.append(new_function)

            elif node_.type == "function_definition":
                function_name = ""

                function_declarator_node = ts_find_child_node_by_type(
                    node_, "function_declarator"
                )
                # C++ reference declaration wrap the function declaration one time.
                if function_declarator_node is None:
                    # Example: Foo& Foo::operator+(const Foo& c) { return *this; }
                    reference_declarator_node = ts_find_child_node_by_type(
                        node_, "reference_declarator"
                    )
                    if reference_declarator_node is None:
                        continue

                    function_declarator_node = ts_find_child_node_by_type(
                        reference_declarator_node, "function_declarator"
                    )
                    if function_declarator_node is None:
                        continue

                assert function_declarator_node is not None, node_.text

                assert function_declarator_node.text is not None, node_.text
                function_name = function_declarator_node.text.decode("utf8")

                identifier_node = self._get_function_name_node(
                    function_declarator_node
                )
                if identifier_node is None:
                    raise NotImplementedError(function_declarator_node)

                assert identifier_node.text is not None, node_.text
                function_display_name = identifier_node.text.decode("utf8")

                assert function_name is not None, node_.text
                parent_names = self.get_node_ns(node_)
                if len(parent_names) > 0:
                    function_name = (
                        f"{'::'.join(parent_names)}::{function_name}"
                    )
                    function_display_name = (
                        f"{'::'.join(parent_names)}::{function_display_name}"
                    )

                # FIXME: Special hack for Google Test macros TEST, TEST_F, TEST_P.
                if function_name.startswith("TEST"):
                    function_display_name = function_name

                function_markers = []
                function_comment_node = None
                function_comment_text = None

                # In the condition below, it is important that the comment is
                # considered a function comment only if it there are no empty
                # lines between the comment and function.
                if (
                    node_.prev_sibling is not None
                    and node_.prev_sibling.type == "comment"
                    and (node_.prev_sibling.end_point[0] + 1)
                    == node_.start_point[0]
                ):
                    function_comment_node = node_.prev_sibling
                    assert function_comment_node.text is not None, node_.text
                    function_comment_text = function_comment_node.text.decode(
                        "utf8"
                    )

                    function_last_line = node_.end_point[0] + 1

                    source_node = MarkerParser.parse(
                        function_comment_text,
                        function_comment_node.start_point[0] + 1,
                        function_last_line,
                        function_comment_node.start_point[0] + 1,
                        entity_name=function_display_name,
                        parse_nodes=self.parse_nodes,
                    )
                    traceability_info.source_nodes.append(source_node)
                    for marker_ in source_node.markers:
                        if isinstance(marker_, FunctionRangeMarker):
                            function_range_marker_processor(
                                marker_, parse_context
                            )
                            traceability_info.markers.append(marker_)
                            function_markers.append(marker_)

                # The function range includes the top comment if it exists.
                new_function = Function(
                    parent=traceability_info,
                    name=function_name,
                    display_name=function_display_name,
                    line_begin=function_comment_node.start_point[0] + 1
                    if function_comment_node is not None
                    else node_.range.start_point[0] + 1,
                    line_end=node_.range.end_point[0] + 1,
                    child_functions=[],
                    markers=function_markers,
                    attributes={FunctionAttribute.DEFINITION},
                )
                traceability_info.functions.append(new_function)
                if len(function_markers) > 0:
                    traceability_info.ng_map_names_to_markers[function_name] = (
                        # FIXME: Cannot win the fight with mypy without assert_cast.
                        assert_cast(function_markers, list)
                    )
                    traceability_info.ng_map_names_to_definition_functions[
                        function_name
                    ] = new_function
            elif node_.type == "comment":
                #
                # FIXME: Here parsing of function comments can happen as well
                #        but this time the focus is ONLY on range and line markers.
                #        The case which is handled here is when a user adds a
                #        range_start marker in a function comment.
                #        It is not good that parsing of function comments
                #        happens twice.
                #

                assert node_.text is not None, (
                    f"Comment without a text: {node_}"
                )

                node_text_string = node_.text.decode("utf8")

                source_node = MarkerParser.parse(
                    node_text_string,
                    node_.start_point[0] + 1,
                    node_.end_point[0] + 1,
                    node_.start_point[0] + 1,
                    parse_nodes=False,
                )

                for marker_ in source_node.markers:
                    if isinstance(marker_, RangeMarker) and (
                        range_marker_ := marker_
                    ):
                        range_marker_processor(range_marker_, parse_context)
                    elif isinstance(marker_, LineMarker) and (
                        line_marker_ := marker_
                    ):
                        line_marker_processor(line_marker_, parse_context)
                    else:
                        pass
            else:
                pass

        source_file_traceability_info_processor(
            traceability_info, parse_context
        )

        traceability_info.ng_map_reqs_to_markers = (
            parse_context.map_reqs_to_markers
        )

        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        try:
            with open(file_path, "rb") as file:
                sdoc_content = file.read()
                sdoc = self.read(sdoc_content, file_path=file_path)
                return sdoc
        except UnicodeDecodeError:
            raise
        except NotImplementedError:
            traceback.print_exc()
            sys.exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(  # noqa: T201
                f"error: SourceFileTraceabilityReader_C: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def _get_function_name_node(
        function_declarator_node: Node,
    ) -> Optional[Node]:
        assert function_declarator_node.type == "function_declarator"
        function_identifier_node = ts_find_child_node_by_type(
            function_declarator_node,
            node_type=(
                "identifier",
                "field_identifier",
                "operator_name",
                "destructor_name",
                "qualified_identifier",
            ),
        )
        return function_identifier_node

    @staticmethod
    def get_node_ns(node: Node) -> Sequence[str]:
        """
        Walk up the tree and find parent classes.
        """
        parent_scopes = []
        cursor: Optional[Node] = node
        while cursor is not None:
            if cursor.type == "class_specifier" and len(cursor.children) > 1:
                second_node_or_none = cursor.children[1]
                if (
                    second_node_or_none.type == "type_identifier"
                    and second_node_or_none.text is not None
                ):
                    parent_class_name = second_node_or_none.text.decode("utf8")
                    parent_scopes.append(parent_class_name)

            cursor = cursor.parent

        parent_scopes.reverse()
        return parent_scopes
