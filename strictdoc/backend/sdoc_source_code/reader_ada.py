"""
@relation(SDOC-SRS-142, SDOC-SRS-208, scope=file)
"""

import re
from typing import Dict, List, Optional

import tree_sitter_ada
from tree_sitter import Language, Node, Parser

from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.language import LanguageItem
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
    RangeMarkerType,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.models.source_location import ByteRange
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    language_item_marker_processor,
    line_marker_processor,
    range_marker_processor,
    source_file_traceability_info_processor,
)
from strictdoc.backend.sdoc_source_code.tree_sitter_helpers import (
    traverse_tree,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_stats import SourceFileStats
from strictdoc.helpers.file_system import file_open_read_bytes

SUBPROGRAM_DECLARATIONS = (
    "subprogram_declaration",
    "generic_subprogram_declaration",
)
SUBPROGRAM_DEFINITIONS = (
    "subprogram_body",
    "null_procedure_declaration",
    "expression_function_declaration",
)
SPECIFICATIONS = ("procedure_specification", "function_specification")


class SourceFileTraceabilityReader_Ada:
    @staticmethod
    def supported_elements() -> list[str]:
        return ["function"]

    def __init__(self, custom_tags: Optional[set[str]] = None) -> None:
        self.custom_tags: Optional[set[str]] = custom_tags

    def read(
        self,
        input_buffer: bytes,
        file_path: Optional[str] = None,
    ) -> SourceFileTraceabilityInfo:
        assert isinstance(input_buffer, bytes)

        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)
        parser = Parser(Language(tree_sitter_ada.language()))
        tree = parser.parse(input_buffer)

        traceability_info = SourceFileTraceabilityInfo([])

        # Ada has only "--" line comments, one tree-sitter node per line.
        # Consecutive full-line comments form one comment block. A comment
        # after code on the same line is a block of its own.
        comment_blocks: List[List[Node]] = []
        trailing_comment_lines: set[int] = set()
        subprogram_nodes: List[Node] = []
        for node_ in traverse_tree(tree):
            if node_.type == "comment":
                if self._is_trailing_comment(input_buffer, node_):
                    trailing_comment_lines.add(node_.start_point[0])
                    comment_blocks.append([node_])
                elif (
                    len(comment_blocks) > 0
                    and comment_blocks[-1][-1].start_point[0] + 1
                    == node_.start_point[0]
                    and node_.start_point[0] - 1 not in trailing_comment_lines
                ):
                    comment_blocks[-1].append(node_)
                else:
                    comment_blocks.append([node_])
            elif node_.type in SUBPROGRAM_DECLARATIONS + SUBPROGRAM_DEFINITIONS:
                subprogram_nodes.append(node_)

        blocks_by_last_line: Dict[int, List[Node]] = {
            block_[-1].start_point[0]: block_
            for block_ in comment_blocks
            if block_[-1].start_point[0] not in trailing_comment_lines
        }
        attached_blocks: set[int] = set()

        root_node = tree.root_node
        if (
            len(comment_blocks) > 0
            and len(root_node.children) > 0
            and root_node.children[0] == comment_blocks[0][0]
        ):
            file_source_node = self._parse_comment_block(
                input_buffer,
                comment_blocks[0],
                line_end=file_stats.lines_total,
                parse_context=parse_context,
                custom_tags=self.custom_tags,
            )
            for marker_ in file_source_node.markers:
                if (
                    isinstance(marker_, LanguageItemMarker)
                    and marker_.scope == RangeMarkerType.FILE
                ):
                    language_item_marker_processor(marker_, parse_context)
                    traceability_info.markers.append(marker_)

        for node_ in subprogram_nodes:
            specification_node = self._find_specification_node(node_)
            if specification_node is None:
                continue
            name_node = specification_node.child_by_field_name("name")
            if name_node is None:
                continue
            function_display_name = ".".join(
                [*self._get_parent_names(node_), self._node_text(name_node)]
            )
            # Ada names are case-insensitive. The lower-case name is the key
            # for linking a body to its declaration.
            function_name = function_display_name.lower()
            is_definition = node_.type in SUBPROGRAM_DEFINITIONS

            comment_block = blocks_by_last_line.get(node_.start_point[0] - 1)
            language_item_markers: List[LanguageItemMarker] = []
            source_node: Optional[SourceNode] = None
            if comment_block is not None:
                attached_blocks.add(comment_block[0].start_byte)
                source_node = self._parse_comment_block(
                    input_buffer,
                    comment_block,
                    line_end=node_.end_point[0] + 1,
                    parse_context=parse_context,
                    entity_name=function_display_name,
                    custom_tags=self.custom_tags,
                )
                if is_definition:
                    traceability_info.source_nodes.append(source_node)
                for marker_ in source_node.markers:
                    if isinstance(marker_, LanguageItemMarker):
                        language_item_marker_processor(marker_, parse_context)
                        traceability_info.markers.append(marker_)
                        language_item_markers.append(marker_)

            start_node = (
                comment_block[0] if comment_block is not None else node_
            )
            new_function = LanguageItem(
                parent=traceability_info,
                name=function_name,
                display_name=function_display_name,
                line_begin=start_node.start_point[0] + 1,
                line_end=node_.end_point[0] + 1,
                code_byte_range=ByteRange.create_from_ts_node(node_),
                child_functions=[],
                markers=language_item_markers,
                attributes={
                    FunctionAttribute.DEFINITION
                    if is_definition
                    else FunctionAttribute.DECLARATION
                },
            )
            if source_node is not None:
                source_node.function = new_function
            traceability_info.functions.append(new_function)

        for block_ in comment_blocks:
            source_node = self._parse_comment_block(
                input_buffer,
                block_,
                line_end=block_[-1].end_point[0] + 1,
                parse_context=parse_context,
            )
            for marker_ in source_node.markers:
                if isinstance(marker_, RangeMarker):
                    range_marker_processor(marker_, parse_context)
                elif isinstance(marker_, LineMarker):
                    line_marker_processor(marker_, parse_context)
                elif (
                    isinstance(marker_, LanguageItemMarker)
                    and marker_.scope == RangeMarkerType.FUNCTION
                    and block_[0].start_byte not in attached_blocks
                ):
                    print(  # noqa: T201
                        "warning: Ada source reader: "
                        f"{parse_context.filename}:"
                        f"{marker_.ng_source_line_begin}: "
                        "skipping a scope=function marker for "
                        f"{', '.join(marker_.reqs)}: "
                        "no subprogram found directly below the comment."
                    )

        source_file_traceability_info_processor(
            traceability_info, parse_context
        )

        traceability_info.ng_map_reqs_to_markers = (
            parse_context.map_reqs_to_markers
        )

        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        with file_open_read_bytes(file_path) as file:
            sdoc_content = file.read()
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc

    def _parse_comment_block(
        self,
        input_buffer: bytes,
        comment_block: List[Node],
        line_end: int,
        parse_context: ParseContext,
        entity_name: Optional[str] = None,
        custom_tags: Optional[set[str]] = None,
    ) -> SourceNode:
        line_start = comment_block[0].start_point[0] + 1
        comment_bytes = input_buffer[
            comment_block[0].start_byte : comment_block[-1].end_byte
        ]
        # The common comment preprocessor does not know "--". Blank it out
        # with the same length to keep the byte offsets for write-back.
        comment_text = re.sub(
            r"^(\s*)--",
            lambda match_: " " * len(match_.group(0)),
            comment_bytes.decode("utf8"),
            flags=re.MULTILINE,
        )
        return MarkerParser.parse(
            input_string=comment_text,
            line_start=line_start,
            line_end=line_end,
            comment_line_start=line_start,
            comment_byte_range=ByteRange.create_from_ts_nodes(
                comment_block[0], comment_block[-1]
            ),
            filename=parse_context.filename,
            entity_name=entity_name,
            custom_tags=custom_tags,
        )

    @staticmethod
    def _is_trailing_comment(input_buffer: bytes, node: Node) -> bool:
        line_start_byte = input_buffer.rfind(b"\n", 0, node.start_byte) + 1
        return len(input_buffer[line_start_byte : node.start_byte].strip()) > 0

    @staticmethod
    def _find_specification_node(node: Node) -> Optional[Node]:
        for child_ in node.children:
            if child_.type in SPECIFICATIONS:
                return child_
        return None

    @staticmethod
    def _get_parent_names(node: Node) -> List[str]:
        """
        Collect the names of the enclosing packages and subprograms, outermost
        first, to build the Ada expanded name, e.g. "Pkg.Inner.Proc".
        """
        parent_names = []
        cursor = node.parent
        while cursor is not None:
            name_node = None
            if cursor.type in ("package_declaration", "package_body"):
                name_node = cursor.child_by_field_name("name")
            elif cursor.type == "subprogram_body":
                specification_node = (
                    SourceFileTraceabilityReader_Ada._find_specification_node(
                        cursor
                    )
                )
                if specification_node is not None:
                    name_node = specification_node.child_by_field_name("name")
            elif cursor.type == "subunit":
                name_node = cursor.named_children[0]
            if name_node is not None:
                parent_names.append(
                    SourceFileTraceabilityReader_Ada._node_text(name_node)
                )
            cursor = cursor.parent
        parent_names.reverse()
        return parent_names

    @staticmethod
    def _node_text(node: Node) -> str:
        return assert_cast(node.text, bytes).decode("utf8")
