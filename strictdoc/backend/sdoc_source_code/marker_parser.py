"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

from typing import Dict, List, Optional, Tuple, Union

from lark import ParseTree, Token, Tree

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.comment_parser.marker_lexer import (
    MarkerLexer,
)
from strictdoc.backend.sdoc_source_code.helpers.comment_preprocessor import (
    preprocess_source_code_comment,
)
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.models.source_location import ByteRange
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode


class MarkerParser:
    @staticmethod
    def parse(
        *,
        input_string: str,
        line_start: int,
        line_end: int,
        comment_line_start: int,
        comment_byte_range: Optional[ByteRange],
        filename: Optional[str] = None,
        entity_name: Optional[str] = None,
        col_offset: int = 0,
        custom_tags: Optional[set[str]] = None,
        default_scope: Optional[str] = None,
    ) -> SourceNode:
        """
        Parse source nodes and relation markers from source file comments.

        Before the actual parsing, the function removes all code comment symbols
        such as /** ... */ or /// Doxygen comments or Python

        The 1-based line start/end provide hints to the parser for the case markers
        of scope file, class or function are found, in which case the user values are
        set as highlight range. If the parser finds line or range markers, the user
        provided line start/end values are ignored. Should be set to the item definition
        block, *with* leading comment lines if any.

        The 1-based comment_line_start parameter is the first actual comment line.
        It is required as a base offset for some parser tokens to determine their
        absolute position in file, as lexing gives only a position relative
        to comment start.

        custom_tags is a set of valid tags if a comment is expected to contain
        key-value pairs for source node generation. The caller is responsible to determine
        valid custom tags from the grammar element associated with the source code file.

        filename should be given if input_string comes from a static source file.
        It will be used to create more helpful parsing error messages.

        entity_name is required for language item markers. It's the user-visible
        description of the marked range in the rendered document. Should be equal
        to the related LanguageItem.description for consistency with forward markers.

        default_scope should be provided if the caller's language-aware parser
        can infer the scope from the semantic comment position. Think of Rust doc
        comments for example. If given, users are allowed to omit the scope argument
        in a relation marker. A user provided scope argument always takes preference.
        If neither default nor a user provided value is available,
        StrictDocSemanticError will be raised.

        The function returns a SourceNode. Note: This is also the case if no custom tags were
        found at all (in which case fields is empty) because SourceNode also acts as a container
        for markers.
        """

        node_fields: Dict[str, str] = {}

        source_node: SourceNode = SourceNode(
            entity_name=entity_name,
            comment_byte_range=comment_byte_range,
        )
        input_string = preprocess_source_code_comment(input_string)

        tree: ParseTree = MarkerLexer.parse(
            input_string, custom_tags=custom_tags
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
                    filename,
                    entity_name,
                    col_offset,
                    default_scope,
                )
                source_node.markers.extend(relation_markers)

            elif element_.data == "node_field":
                node_name, node_value = MarkerParser._parse_node_field(
                    element_,
                )
                node_fields[node_name] = node_value

                source_node.fields_locations[node_name] = (
                    element_.meta.start_pos,
                    element_.meta.end_pos - 1,
                )
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
        filename: Optional[str] = None,
        entity_name: Optional[str] = None,
        col_offset: int = 0,
        default_scope: Optional[str] = None,
    ) -> List[Union[LanguageItemMarker, RangeMarker, LineMarker]]:
        markers: List[Union[LanguageItemMarker, RangeMarker, LineMarker]] = []

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

        if relation_scope_element is not None:
            assert isinstance(relation_scope_element.children[0], Token)
            relation_scope = relation_scope_element.children[0].value
        else:
            relation_scope = default_scope

        relation_role = None
        if relation_role_element is not None:
            assert isinstance(relation_role_element.children[0], Token)
            relation_role = relation_role_element.children[0].value

        requirements = []
        used_uids = set()

        for relation_uid_token_ in relation_uid_elements:
            assert isinstance(relation_uid_token_.children[0], Token)
            relation_uid = relation_uid_token_.children[0].value
            if relation_uid in used_uids:
                raise ValueError(
                    f"@relation marker contains duplicate node UIDs: ['{relation_uid}']."
                )
            used_uids.add(relation_uid)

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
            language_item_marker = LanguageItemMarker(
                None, requirements, scope=relation_scope, role=relation_role
            )
            language_item_marker.ng_source_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            language_item_marker.ng_source_column_begin = (
                element_.meta.column + col_offset
            )
            language_item_marker.ng_range_line_begin = line_start
            language_item_marker.ng_range_line_end = line_end
            if relation_scope == "file":
                language_item_marker.set_description("entire file")
            elif relation_scope == "function":
                language_item_marker.set_description(
                    f"function {entity_name}()"
                )
            elif relation_scope == "class":
                language_item_marker.set_description(f"class {entity_name}")
            markers.append(language_item_marker)
        elif relation_scope in ("range_start", "range_end"):
            range_marker = RangeMarker(
                None,
                requirements,
                scope=relation_scope,
                role=relation_role,
            )
            range_marker.ng_source_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            range_marker.ng_source_column_begin = (
                element_.meta.column + col_offset
            )
            range_marker.ng_range_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            range_marker.ng_range_line_end = (
                comment_line_start + element_.meta.end_line - 1
            )
            markers.append(range_marker)
        elif relation_scope == "line":
            line_marker = LineMarker(None, requirements, role=relation_role)
            line_marker.ng_source_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            line_marker.ng_source_column_begin = (
                element_.meta.column + col_offset
            )
            line_marker.ng_range_line_begin = (
                comment_line_start + element_.meta.line - 1
            )
            line_marker.ng_range_line_end = (
                comment_line_start + element_.meta.end_line
            )
            markers.append(line_marker)
        elif relation_scope is None:
            reqs = ",".join(sorted(used_uids))
            raise StrictDocSemanticError(
                f"@relation marker for requirements {reqs} misses scope argument.",
                hint="Scope can only be omitted if supported by language, as e.g. with Rust doc comments.",
                example=(
                    "Add a scope argument. Example:\n"
                    f"@relation({reqs}, scope=function)"
                ),
                line=comment_line_start + element_.meta.line - 1,
                filename=filename,
            )
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

        # Find minimal indent in lines 1..n. It will be used to dedent the block.
        dedent = None
        if len(node_value_node.children) > 1:
            for node_value_component_ in node_value_node.children[1:]:
                assert isinstance(node_value_component_, Token)
                if node_value_component_.type == "NEWLINE":
                    continue
                line_value = node_value_component_.value
                non_ws_len = len(line_value.lstrip(" "))
                this_dedent = len(line_value) - non_ws_len
                if dedent is None:
                    dedent = this_dedent
                elif non_ws_len > 0:
                    dedent = min(this_dedent, dedent)
        if dedent is None:
            dedent = 0

        # Join and dedent.
        node_value = ""
        for i, node_value_component_ in enumerate(node_value_node.children):
            assert isinstance(node_value_component_, Token)
            line_value = node_value_component_.value
            if (
                i > 0
                and node_value_component_.type != "NEWLINE"
                and dedent is not None
            ):
                line_value = line_value[min(dedent, len(line_value)) :]
            node_value += line_value

        node_value = node_value.rstrip()

        return node_name, node_value
