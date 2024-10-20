# mypy: disable-error-code="no-any-return,no-untyped-call,no-untyped-def,union-attr"
from dataclasses import dataclass
from datetime import datetime
from typing import List, NamedTuple, Union

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    LineMarker,
    RangeMarker,
)
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class SourceMarkerTuple(NamedTuple):
    before_line: Markup
    after_line: Markup
    marker: Union[ForwardRangeMarker, LineMarker, RangeMarker]


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

        self.standalone: bool = False
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(traceability_index.document_tree)
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/source_file_view/index.jinja", view_object=self
        )

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def render_url(self, url: str):
        return self.link_renderer.render_url(url)

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
