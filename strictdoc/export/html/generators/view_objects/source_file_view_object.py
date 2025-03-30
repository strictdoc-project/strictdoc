# mypy: disable-error-code="no-any-return,no-untyped-call,no-untyped-def,union-attr"
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union, Optional

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document_view import NullViewElement
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    LineMarker,
    RangeMarker,
)
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.source_tree import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


@dataclass
class SourceMarkerTuple:
    ng_range_line_begin: int
    ng_range_line_end: int
    source_line: Markup
    markers: List[
        Union[FunctionRangeMarker, ForwardRangeMarker, LineMarker, RangeMarker]
    ]

    def is_end(self) -> bool:
        return any(map(lambda m_: m_.is_end(), self.markers))

    def is_line_marker(self) -> bool:
        return any(map(lambda m_: isinstance(m_, LineMarker), self.markers))


SourceLineEntry = Union[
    Markup,
    SourceMarkerTuple,
]


@dataclass
class SourceFileViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        link_renderer: LinkRenderer,
        markup_renderer: MarkupRenderer,
        source_file: SourceFile,
        pygments_styles: Markup,
        pygmented_source_file_lines: List[SourceLineEntry],
        jinja_environment: JinjaEnvironment,
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.source_file: SourceFile = source_file
        self.pygments_styles: Markup = pygments_styles
        self.pygmented_source_file_lines: List[SourceLineEntry] = (
            pygmented_source_file_lines
        )
        self.jinja_environment: JinjaEnvironment = jinja_environment

        self.current_view = NullViewElement()
        self.standalone: bool = False
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(traceability_index.document_tree)
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def render_screen(self) -> Markup:
        return self.jinja_environment.render_template_as_markup(
            "screens/source_file_view/index.jinja", view_object=self
        )

    def render_detailed_node_for_banner(self, node_uid: str) -> Markup:
        node: SDocNode = self.traceability_index.get_node_by_uid(node_uid)
        return self.jinja_environment.render_template_as_markup(
            "components/requirement/index_extends_readonly.jinja",
            node=node,
            view_object=self,
            requirement_style="table",
        )

    def render_node_title_for_banner_header(self, node_uid: str, role: Optional[str]) -> Markup:
        node: SDocNode = self.traceability_index.get_node_by_uid(node_uid)
        # return node.reserved_title + ' ' + node.node_type
        return self.jinja_environment.render_template_as_markup(
            "screens/source_file_view/node_title_for_banner_header.jinja",
            node=node,
            view_object=self,
            role=role,
        )

    def render_aside_requirement(self, node_uid: str, range_begin: str, range_end: str) -> Markup:
        node: SDocNode = self.traceability_index.get_node_by_uid(node_uid)
        return self.jinja_environment.render_template_as_markup(
            "screens/source_file_view/requirement.jinja",
            requirement=node,
            view_object=self,
            requirement_style="table",
            range_begin=range_begin,
            range_end=range_end,
        )

    def render_node_title(self, node: SDocNode) -> Markup:
        return Markup(node.get_display_title())

    def render_node_statement(self, node: SDocNode) -> Markup:
        return self.markup_renderer.render_node_statement(
            DocumentType.document(), node
        )

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def render_url(self, url: str):
        return self.link_renderer.render_url(url)

    def render_marker_range_link(self, marker):
        return self.link_renderer.render_requirement_in_source_file_range_link(
            self.source_file.in_doctree_source_file_rel_path_posix,
            self.source_file,
            marker,
        )

    def render_node_link(self, incoming_link, document, document_type):
        return self.link_renderer.render_node_link(
            incoming_link, document, document_type
        )

    def render_static_url(self, url: str):
        return self.link_renderer.render_static_url(url)

    def render_local_anchor(self, node):
        return self.link_renderer.render_local_anchor(node)

    def date_today(self):
        return datetime.today().strftime("%Y-%m-%d")

    def get_document_by_path(self, full_path: str):
        return self.traceability_index.document_tree.get_document_by_path(
            full_path
        )
