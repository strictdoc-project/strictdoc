# mypy: disable-error-code="no-any-return,no-untyped-call,no-untyped-def"
from dataclasses import dataclass
from datetime import datetime

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.project_tree_stats import (
    DocumentTreeStats,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


@dataclass
class ProjectStatisticsViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        link_renderer: LinkRenderer,
        document_tree_stats: DocumentTreeStats,
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.document_tree_stats: DocumentTreeStats = document_tree_stats
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(traceability_index.document_tree)
        )
        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/project_statistics/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_static_url_with_prefix(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url_with_prefix(url))

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def get_datetime(self) -> str:
        return datetime.today().strftime("%Y-%m-%d %H:%M:%S")
