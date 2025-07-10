"""
@relation(SDOC-SRS-142, scope=file)
"""

import sys
from typing import Union

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
from strictdoc.helpers.file_stats import SourceFileStats


class SdocRelationVisitor(ModelVisitor):
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
    ):
        super().__init__()
        self.traceability_info = traceability_info
        self.parse_context = parse_context

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
        tc_markers = []
        for stmt in node.body:
            if isinstance(stmt, EmptyLine):
                # Trim trailing newlines from test case range.
                trailing_empty_lines += 1
            else:
                trailing_empty_lines = 0

            if isinstance(stmt, (Comment, Tags, Documentation)):
                for token in filter(self._token_filter, stmt.tokens):
                    source_node = MarkerParser.parse(
                        token.value,
                        token.lineno,
                        token.lineno,
                        token.lineno,
                        node.name,
                        token.col_offset,
                    )
                    tc_markers.extend(source_node.markers)

        function_markers = []
        for marker_ in tc_markers:
            if isinstance(marker_, FunctionRangeMarker):
                marker_.ng_range_line_begin = node.lineno
                marker_.ng_range_line_end = (
                    node.end_lineno - trailing_empty_lines
                )
                function_markers.append(marker_)
                function_range_marker_processor(marker_, self.parse_context)
            elif isinstance(marker_, RangeMarker):
                range_marker_processor(marker_, self.parse_context)
            elif isinstance(marker_, LineMarker):
                line_marker_processor(marker_, self.parse_context)

        self.traceability_info.markers.extend(function_markers)
        test_case = Function(
            parent=self.traceability_info,
            name=node.name,
            display_name=node.name,
            line_begin=node.lineno,
            line_end=node.end_lineno - trailing_empty_lines,
            child_functions=[],
            markers=function_markers,
            attributes={FunctionAttribute.DEFINITION},
        )
        self.traceability_info.functions.append(test_case)

    def _visit_possibly_marked_node(
        self, node: Union[Comment, Documentation, Tags]
    ) -> None:
        for token in filter(self._token_filter, node.tokens):
            source_node = MarkerParser.parse(
                token.value,
                node.lineno,
                node.lineno,
                node.lineno,
                None,
                token.col_offset,
            )
            for marker_ in source_node.markers:
                if (
                    isinstance(marker_, FunctionRangeMarker)
                    and marker_.scope is RangeMarkerType.FILE
                ):
                    # Outside Test Cases only accept scope=file function markers
                    marker_.ng_range_line_begin = 1
                    marker_.ng_range_line_end = (
                        self.parse_context.file_stats.lines_total
                    )
                    function_range_marker_processor(marker_, self.parse_context)
                    self.traceability_info.markers.append(marker_)
                elif isinstance(marker_, RangeMarker):
                    range_marker_processor(marker_, self.parse_context)
                elif isinstance(marker_, LineMarker):
                    line_marker_processor(marker_, self.parse_context)

    @staticmethod
    def _token_filter(token: Token) -> bool:
        if token.type in ("SEPARATOR", "EOL"):
            return False
        return True


class SourceFileTraceabilityReader_Robot:
    def read(
        self, input_buffer: str, file_path: str
    ) -> SourceFileTraceabilityInfo:
        traceability_info = SourceFileTraceabilityInfo([])
        if len(input_buffer) == 0:
            return traceability_info
        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)
        robotfw_model = get_model(input_buffer, data_only=False)
        visitor = SdocRelationVisitor(traceability_info, parse_context)
        visitor.visit(robotfw_model)
        source_file_traceability_info_processor(
            traceability_info, parse_context
        )
        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        try:
            with open(file_path) as file:
                sdoc_content = file.read()
                sdoc = self.read(sdoc_content, file_path=file_path)
                return sdoc
        except UnicodeDecodeError:
            raise
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(  # noqa: T201
                f"error: SourceFileTraceabilityReader_Robot: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided
            # traceback.print_exc()  # noqa: ERA001
            sys.exit(1)
