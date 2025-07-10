"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

from typing import Dict, List, Optional, Tuple, Union

from lark import ParseTree, Token, Tree

from strictdoc.backend.sdoc_source_code.comment_parser.marker_lexer import (
    MarkerLexer,
)
from strictdoc.backend.sdoc_source_code.helpers.comment_preprocessor import (
    preprocess_source_code_comment,
)
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode


class MarkerParser:
    @staticmethod
    def parse(
        input_string: str,
        line_start: int,
        line_end: int,
        comment_line_start: int,
        entity_name: Optional[str] = None,
        col_offset: int = 0,
        parse_nodes: bool = False,
    ) -> SourceNode:
        """
        Parse relation markers from source file comments.

        Before the actual parsing, the function removes all code comment symbols
        such as /** ... */ or /// Doxygen comments or Python

        The line start/end indicate a range where the comment is located in the
        source file.
        The comment_line_start parameter maybe the same as line start but can
        also be different if the comment is part of a Python or C function in
        which case the comment_line_start will be several lines below the actual
        start of the range.
        """

        node_fields: Dict[str, str] = {}
        source_node: SourceNode = SourceNode(entity_name)

        input_string = preprocess_source_code_comment(input_string)

        tree: ParseTree = MarkerLexer.parse(
            input_string, parse_nodes=parse_nodes
        )

        for element_ in tree.children:
            if not isinstance(element_, Tree):
                continue

            if element_.data == "relation_marker":
                relation_markers = MarkerParser._parse_relation_marker(
                    element_,
                    line_start,
                    line_end,
                    comment_line_start,
                    entity_name,
                    col_offset,
                )
                source_node.markers.extend(relation_markers)

            elif element_.data == "node_field":
                node_name, node_value = MarkerParser._parse_node_field(
                    element_,
                )
                node_fields[node_name] = node_value
            else:
                raise AssertionError

        if len(node_fields) > 0:
            source_node.fields = node_fields

        return source_node

    @staticmethod
    def _parse_relation_marker(
        element_: Tree[Token],
        line_start: int,
        line_end: int,
        comment_line_start: int,
        entity_name: Optional[str] = None,
        col_offset: int = 0,
    ) -> List[Union[FunctionRangeMarker, RangeMarker, LineMarker]]:
        markers: List[Union[FunctionRangeMarker, RangeMarker, LineMarker]] = []

        relation_uid_elements = []
        relation_scope_element: Optional[Tree[Token]] = None
        relation_role_element: Optional[Tree[Token]] = None
        for relation_marker_element_ in element_.children:
            assert isinstance(relation_marker_element_, Tree)
            if relation_marker_element_.data == "relation_node_uid":
                relation_uid_elements.append(relation_marker_element_)
            elif relation_marker_element_.data == "relation_scope":
                relation_scope_element = relation_marker_element_
            elif relation_marker_element_.data == "relation_role":
                relation_role_element = relation_marker_element_
            else:
                raise NotImplementedError

        assert len(relation_uid_elements) > 0
        assert relation_scope_element is not None

        assert isinstance(relation_scope_element.children[0], Token)
        relation_scope = relation_scope_element.children[0].value

        relation_role = None
        if relation_role_element is not None:
            assert isinstance(relation_role_element.children[0], Token)
            relation_role = relation_role_element.children[0].value

        requirements = []
        for relation_uid_token_ in relation_uid_elements:
            assert isinstance(relation_uid_token_.children[0], Token)
            relation_uid = relation_uid_token_.children[0].value

            assert relation_uid_token_.children[0].line is not None
            requirement = Req(None, relation_uid)
            requirement.ng_source_line = (
                comment_line_start + relation_uid_token_.children[0].line - 1
            )
            requirement.ng_source_column = relation_uid_token_.children[
                0
            ].column
            requirements.append(requirement)

        if relation_scope in ("file", "class", "function"):
            function_marker = FunctionRangeMarker(
                None, requirements, scope=relation_scope, role=relation_role
            )
            function_marker.ng_source_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            function_marker.ng_source_column_begin = (
                element_.meta.column + col_offset
            )
            function_marker.ng_range_line_begin = line_start
            function_marker.ng_range_line_end = line_end
            if relation_scope == "file":
                function_marker.set_description("entire file")
            elif relation_scope == "function":
                function_marker.set_description(f"function {entity_name}()")
            elif relation_scope == "class":
                function_marker.set_description(f"class {entity_name}")
            markers.append(function_marker)
        elif relation_scope in ("range_start", "range_end"):
            start_or_end = relation_scope == "range_start"
            range_marker = RangeMarker(
                None,
                "[" if start_or_end else "[/",
                requirements,
                role=relation_role,
            )
            range_marker.ng_source_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            range_marker.ng_source_column_begin = (
                element_.meta.column + col_offset
            )
            range_marker.ng_range_line_begin = line_start
            range_marker.ng_range_line_end = line_end
            range_marker.ng_new_relation_keyword = True
            markers.append(range_marker)
        elif relation_scope == "line":
            line_marker = LineMarker(None, requirements, role=relation_role)
            line_marker.ng_source_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            line_marker.ng_source_column_begin = (
                element_.meta.column + col_offset
            )
            line_marker.ng_range_line_begin = line_start
            line_marker.ng_range_line_end = line_end
            markers.append(line_marker)
        else:
            raise NotImplementedError

        return markers

    @staticmethod
    def _parse_node_field(
        element_: Tree[Token],
    ) -> Tuple[str, str]:
        node_name_node = element_.children[0]
        assert isinstance(node_name_node, Tree)
        assert node_name_node.data == "node_name"
        assert isinstance(node_name_node.children[0], Token)
        node_name = node_name_node.children[0].value

        node_value_node = element_.children[1]
        assert isinstance(node_value_node, Tree)
        assert node_value_node.data == "node_multiline_value"

        processed_node_values = []
        for node_value_component_ in node_value_node.children:
            assert isinstance(node_value_component_, Token)
            processed_node_value = node_value_component_.value.strip()
            if "\\n\\n" in processed_node_value:
                processed_node_value = processed_node_value.replace(
                    "\\n\\n", ""
                )

            processed_node_values.append(processed_node_value)

        node_value = "\n".join(processed_node_values)

        return node_name, node_value
