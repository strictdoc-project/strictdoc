"""
@relation(SDOC-SRS-142, SDOC-SRS-148, scope=file)
"""

from typing import List, Optional, Union

from robot.api.parsing import (
    Comment,
    Documentation,
    EmptyLine,
    ModelVisitor,
    Tags,
    TestCase,
    Token,
    get_model,
)
from robot.parsing.model.statements import Statement

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
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    language_item_marker_processor,
    line_marker_processor,
    range_marker_processor,
    source_file_traceability_info_processor,
)
from strictdoc.helpers.file_stats import SourceFileStats
from strictdoc.helpers.file_system import file_open_read_utf8


class SdocRelationVisitor(ModelVisitor):  # type: ignore[misc]
    """
    Create functions from test cases in *.robot files and create markers.

    Note: ModelVisitor reuses ast.NodeVisitor from Python. We rely on following
    behavior.
    - It traverses depth first. This order is important to get matching marker
      pairs on the ParsersContext.marker_stack.
    - It doesn't recurse into subtrees if a custom visit_* method is defined.
      This is important to avoid duplicated matches.
    """

    def __init__(
        self,
        traceability_info: SourceFileTraceabilityInfo,
        parse_context: ParseContext,
        custom_tags: Optional[set[str]] = None,
    ):
        super().__init__()
        self.traceability_info = traceability_info
        self.parse_context = parse_context
        self.custom_tags = custom_tags

    def visit_Comment(self, node: Comment) -> None:
        """
        Create non-function Marker from Comment outside TestCases.
        """
        self._visit_possibly_marked_node(node)

    def visit_Documentation(self, node: Documentation) -> None:
        """
        Create non-function Marker from Documentation outside TestCases.
        """
        self._visit_possibly_marked_node(node)

    def visit_Tags(self, node: Tags) -> None:
        """
        Create non-function Marker from Tags outside TestCases.
        """
        self._visit_possibly_marked_node(node)

    def visit_TestCase(self, node: TestCase) -> None:
        """
        Create function and non-function Marker from TestCases.
        """
        trailing_empty_lines = 0
        tc_markers: List[
            Union[LanguageItemMarker, RangeMarker, LineMarker]
        ] = []
        tc_source_nodes: List[SourceNode] = []

        for stmt in node.body:
            if isinstance(stmt, EmptyLine):
                # Trim trailing newlines from test case range.
                trailing_empty_lines += 1
            else:
                trailing_empty_lines = 0

            source_node = self._parse_stmt(
                stmt, node.name, node.lineno, node.end_lineno
            )
            if source_node is not None:
                tc_markers.extend(source_node.markers)
                if isinstance(stmt, Documentation) and source_node.fields:
                    tc_source_nodes.append(source_node)

        language_item_markers = []
        for marker_ in tc_markers:
            if isinstance(marker_, LanguageItemMarker):
                marker_.ng_range_line_begin = node.lineno
                marker_.ng_range_line_end = (
                    node.end_lineno - trailing_empty_lines
                )
                language_item_markers.append(marker_)
                language_item_marker_processor(marker_, self.parse_context)
            elif isinstance(marker_, RangeMarker):
                range_marker_processor(marker_, self.parse_context)
            elif isinstance(marker_, LineMarker):
                line_marker_processor(marker_, self.parse_context)

        self.traceability_info.markers.extend(language_item_markers)
        test_case = LanguageItem(
            parent=self.traceability_info,
            name=node.name,
            display_name=node.name,
            line_begin=node.lineno,
            line_end=node.end_lineno - trailing_empty_lines,
            # FIXME: Byte range is currently not used for Robot framework.
            code_byte_range=None,
            child_functions=[],
            markers=language_item_markers,
            attributes={FunctionAttribute.DEFINITION},
        )
        # Link source nodes (parsed from [Documentation] key: value fields)
        # to the test case LanguageItem and register them in traceability_info.
        for source_node in tc_source_nodes:
            source_node.function = test_case
        self.traceability_info.source_nodes.extend(tc_source_nodes)
        self.traceability_info.functions.append(test_case)

    def _visit_possibly_marked_node(
        self, node: Union[Comment, Documentation, Tags]
    ) -> None:
        source_node = self._parse_stmt(node, None, node.lineno, node.end_lineno)
        if source_node is None:
            return
        for marker_ in source_node.markers:
            if (
                isinstance(marker_, LanguageItemMarker)
                and marker_.scope is RangeMarkerType.FILE
            ):
                # Outside Test Cases only accept scope=file function markers
                marker_.ng_range_line_begin = 1
                marker_.ng_range_line_end = (
                    self.parse_context.file_stats.lines_total
                )
                language_item_marker_processor(marker_, self.parse_context)
                self.traceability_info.markers.append(marker_)
            elif isinstance(marker_, RangeMarker):
                range_marker_processor(marker_, self.parse_context)
            elif isinstance(marker_, LineMarker):
                line_marker_processor(marker_, self.parse_context)

    def _parse_stmt(
        self,
        stmt: Statement,
        entity_name: Optional[str],
        line_start: int,
        line_end: int,
    ) -> Optional[SourceNode]:
        if isinstance(stmt, Documentation):
            # Documentation is expected to contain relation markers and source nodes.
            # FIXME: No writeback support for source nodes, because
            #   1) Robot parser doesn't track byte-offsets (lines/columns count characters, not bytes),
            #   2) Line continuation format not handled by MarkerParser.
            return MarkerParser.parse(
                input_string=stmt.value,
                line_start=line_start,
                line_end=line_end,
                comment_byte_range=None,
                filename=self.parse_context.filename,
                comment_line_start=stmt.lineno,
                entity_name=entity_name,
                col_offset=stmt.col_offset,
                custom_tags=self.custom_tags,
            )
        elif isinstance(stmt, (Comment, Tags)):
            # Expect relation markers but no source nodes in comments and tags to keep things simple.
            source_nodes = SourceNode(
                entity_name=entity_name, comment_byte_range=None
            )
            for token in filter(self._token_filter, stmt.tokens):
                sn = MarkerParser.parse(
                    input_string=token.value,
                    line_start=token.lineno,
                    line_end=token.lineno,
                    comment_byte_range=None,
                    filename=self.parse_context.filename,
                    comment_line_start=token.lineno,
                    entity_name=entity_name,
                    col_offset=token.col_offset,
                )
                source_nodes.markers.extend(sn.markers)
            return source_nodes
        return None

    @staticmethod
    def _token_filter(token: Token) -> bool:
        if token.type in ("SEPARATOR", "EOL"):
            return False
        return True


class SourceFileTraceabilityReader_Robot:
    @staticmethod
    def supported_elements() -> list[str]:
        return ["testcase"]

    def __init__(self, custom_tags: Optional[set[str]] = None) -> None:
        self.custom_tags: Optional[set[str]] = custom_tags

    def read(
        self, input_buffer: str, file_path: Optional[str] = None
    ) -> SourceFileTraceabilityInfo:
        traceability_info = SourceFileTraceabilityInfo([])
        if len(input_buffer) == 0:
            return traceability_info
        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)
        robotfw_model = get_model(input_buffer, data_only=False)
        visitor = SdocRelationVisitor(
            traceability_info, parse_context, self.custom_tags
        )
        visitor.visit(robotfw_model)
        source_file_traceability_info_processor(
            traceability_info, parse_context
        )
        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        with file_open_read_utf8(file_path) as file:
            sdoc_content = file.read()
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc
