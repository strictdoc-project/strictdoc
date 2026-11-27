"""
@relation(SDOC-SRS-36, scope=file)
"""

from dataclasses import dataclass
from typing import Any, List, Optional, Union

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_view import NullViewElement
from strictdoc.backend.sdoc.models.model import SDocDocumentIF, SDocNodeIF
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.cast import assert_cast


@dataclass
class SourceMarkerTuple:
    ng_range_line_begin: int
    ng_range_line_end: int
    source_line: Markup
    markers: List[
        Union[LanguageItemMarker, ForwardRangeMarker, LineMarker, RangeMarker]
    ]

    def is_end(self) -> bool:
        return any(map(lambda m_: m_.is_end(), self.markers))

    def is_line_marker(self) -> bool:
        return any(map(lambda m_: isinstance(m_, LineMarker), self.markers))

    def is_range_marker(self) -> bool:
        return any(map(lambda m_: m_.is_range_marker(), self.markers))


SourceLineEntry = Union[
    Markup,
    SourceMarkerTuple,
]


@dataclass
class SourceLine:
    """
    One line of the source file page, ready for main.jinja to print.

    create_source_lines() decides in Python where the ranges open and close,
    so main.jinja only prints the records. The decisions are easier to read,
    test, and debug in Python than in Jinja.
    """

    # The line number, counted from 1.
    number: int
    # The line highlighted by Pygments.
    content: Markup
    # True for an empty line without markers. main.jinja prints a placeholder.
    is_empty: bool
    # The markers whose range header main.jinja prints above the line.
    range_opener: Optional[SourceMarkerTuple]
    # The markers whose range closer main.jinja prints below the line.
    range_closer: Optional[SourceMarkerTuple]


def create_source_lines(entries: List[SourceLineEntry]) -> List[SourceLine]:
    """
    Create one SourceLine per entry and decide where the ranges open and close.

    A range opens above a line with markers, unless the markers only end
    ranges. A range that covers one line has its begin and end markers on the
    same line, so this line opens the range too.

    A range closes below one of these lines:
    - A line with a marker that ends a range.
    - The last line of a line marker: the first line without markers whose
      number is the end of the latest line marker.
    """
    source_lines: List[SourceLine] = []
    # The latest line marker whose range has not closed yet.
    open_line_marker: Optional[SourceMarkerTuple] = None
    for number, entry in enumerate(entries, start=1):
        if isinstance(entry, SourceMarkerTuple):
            opens_range = (
                not entry.is_end()
                or entry.ng_range_line_begin == entry.ng_range_line_end
            )
            closes_range = entry.is_range_marker() and entry.is_end()
            if entry.is_line_marker():
                open_line_marker = entry
            source_lines.append(
                SourceLine(
                    number=number,
                    content=entry.source_line,
                    is_empty=False,
                    range_opener=entry if opens_range else None,
                    range_closer=entry if closes_range else None,
                )
            )
            continue

        range_closer: Optional[SourceMarkerTuple] = None
        if (
            open_line_marker is not None
            and open_line_marker.ng_range_line_end == number
        ):
            range_closer = open_line_marker
            open_line_marker = None
        source_lines.append(
            SourceLine(
                number=number,
                content=entry,
                is_empty=entry == "",
                range_opener=None,
                range_closer=range_closer,
            )
        )
    return source_lines


@dataclass
class SourceFileViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        trace_info: SourceFileTraceabilityInfo,
        project_config: ProjectConfig,
        link_renderer: LinkRenderer,
        markup_renderer: MarkupRenderer,
        text_renderer: MarkupRenderer,
        source_file: SourceFile,
        pygments_styles: Markup,
        pygmented_source_file_lines: List[SourceLineEntry],
        jinja_environment: JinjaEnvironment,
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.trace_info: SourceFileTraceabilityInfo = trace_info
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.text_renderer: MarkupRenderer = text_renderer
        self.source_file: SourceFile = source_file
        self.pygments_styles: Markup = pygments_styles
        self.source_lines: List[SourceLine] = create_source_lines(
            pygmented_source_file_lines
        )
        # The lines that the "Ranges" tab of aside.jinja lists: the lines with
        # markers that begin a range.
        self.range_begin_lines: List[SourceMarkerTuple] = [
            entry_
            for entry_ in pygmented_source_file_lines
            if isinstance(entry_, SourceMarkerTuple) and not entry_.is_end()
        ]
        self.jinja_environment: JinjaEnvironment = jinja_environment

        self.current_view = NullViewElement()
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(
                assert_cast(traceability_index.document_tree, DocumentTree)
            )
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return self.source_file.level

    def render_screen(self) -> Markup:
        return self.jinja_environment.render_template_as_markup(
            "features/source_file_view/index.jinja", view_object=self
        )

    def render_detailed_node_for_banner(self, node_uid: str) -> Markup:
        node: SDocNode = self.traceability_index.get_node_by_uid(node_uid)
        return self.jinja_environment.render_template_as_markup(
            "components/node_content/index_extends_readonly.jinja",
            node=node,
            view_object=self,
            requirement_style="table",
        )

    def render_node_title_for_banner_header(
        self, marker: Union[Any], node_uid: str
    ) -> Markup:
        node: SDocNode = self.traceability_index.get_node_by_uid(node_uid)
        return self.jinja_environment.render_template_as_markup(
            "features/source_file_view/node_title_for_banner_header.jinja",
            node=node,
            view_object=self,
            role=marker.role,
            is_forward_from_requirements_to_code=marker.is_forward(),
        )

    def render_aside_requirement(
        self,
        node_uid: str,
        range_begin: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> Markup:
        node: SDocNode = self.traceability_index.get_node_by_uid(node_uid)
        return self.jinja_environment.render_template_as_markup(
            "features/source_file_view/requirement.jinja",
            requirement=node,
            view_object=self,
            requirement_style="table",
            range_begin=range_begin,
            range_end=range_end,
        )

    def render_node_statement(self, node: SDocNode) -> Markup:
        renderer = self.get_node_renderer(node)
        return renderer.render_node_statement(DocumentType.DOCUMENT, node)

    def render_node_rationale(self, node: SDocNode) -> Markup:
        renderer = self.get_node_renderer(node)
        return renderer.render_node_rationale(DocumentType.DOCUMENT, node)

    def render_node_field(self, node_field: SDocNodeField) -> Markup:
        assert isinstance(node_field, SDocNodeField), node_field
        renderer = (
            self.get_node_renderer(node_field.parent)
            if node_field.parent is not None
            else self.markup_renderer
        )
        return renderer.render_node_field(DocumentType.DOCUMENT, node_field)

    def render_url(self, url: str) -> str:
        return self.link_renderer.render_url(url)

    def render_marker_range_link(self, marker: RangeMarker) -> str:
        return self.link_renderer.render_marker_range_link(
            self.source_file.in_doctree_source_file_rel_path_posix,
            self.source_file,
            marker,
        )

    def render_node_link(self, node: SDocNode) -> str:
        assert isinstance(node, SDocNode), node
        return self.link_renderer.render_requirement_link_from_source_file(
            node, self.source_file
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_local_anchor(
        self, node: Union[Anchor, SDocNode, SDocDocument]
    ) -> str:
        return self.link_renderer.render_local_anchor(node)

    def render_issues(
        self,
        node: Union[SDocNodeIF, SDocDocumentIF],  # noqa: ARG002
        field: Optional[str] = None,  # noqa: ARG002
    ) -> str:
        """
        FIXME: It is not great that this method is called from here.
        """
        return ""

    def get_node_renderer(self, node: SDocNode) -> MarkupRenderer:
        parent_doc = node.get_parent_or_including_document()
        parent_doc_config = parent_doc.config
        if parent_doc_config.markup is SDocMarkup.RST:
            return self.markup_renderer
        return self.text_renderer

    def get_source_file_path(self) -> str:
        return self.source_file.in_doctree_source_file_rel_path_posix

    def get_file_stats_lines_total(self) -> str:
        return str(self.trace_info.file_stats.lines_total)

    def get_file_stats_lines_total_non_empty(self) -> str:
        return str(self.trace_info.file_stats.lines_non_empty)

    def get_file_stats_non_empty_lines_covered(self) -> str:
        covered = self.trace_info.ng_lines_covered
        total_non_empty = self.trace_info.file_stats.lines_non_empty
        percentage = (
            (covered / total_non_empty * 100) if total_non_empty > 0 else 0
        )
        return f"{covered} / {total_non_empty} ({percentage:.1f}%)"

    def get_file_stats_functions_total(self) -> str:
        return str(len(self.trace_info.functions))

    def get_file_stats_functions_covered(self) -> str:
        covered = self.trace_info.covered_functions
        total = len(self.trace_info.functions)
        percentage = (covered / total * 100) if total > 0 else 0
        return f"{covered} / {total} ({percentage:.1f}%)"

    def get_html2pdf_classes(self, node: SDocNode) -> str:  # noqa: ARG002
        """
        This view object class is coupled with the HTML2PDF-related template
        logic.

        The Source File View is not printed with HTML2PDF, so we keep its classes
        to noop.
        """
        return ""
