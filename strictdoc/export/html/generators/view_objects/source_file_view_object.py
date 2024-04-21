# mypy: disable-error-code="no-any-return,no-untyped-call,no-untyped-def,union-attr"
from dataclasses import dataclass
from datetime import datetime
from typing import List

from jinja2 import Environment

from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


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
        pygments_styles: str,
        pygmented_source_file_lines: List[str],
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.source_file: SourceFile = source_file
        self.pygments_styles: str = pygments_styles
        self.pygmented_source_file_lines: List[str] = (
            pygmented_source_file_lines
        )

        self.standalone: bool = False
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(traceability_index.document_tree)
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def render_screen(self, jinja_environment: Environment):
        template = jinja_environment.get_template(
            "screens/source_file_view/index.jinja"
        )
        return template.render(view_object=self)

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

    def render_free_text(self, document_type, free_text):
        return self.markup_renderer.render_free_text(document_type, free_text)

    def date_today(self):
        return datetime.today().strftime("%Y-%m-%d")

    def get_document_by_path(self, full_path: str):
        return self.traceability_index.document_tree.get_document_by_path(
            full_path
        )
