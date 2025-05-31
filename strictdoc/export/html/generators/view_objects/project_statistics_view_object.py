# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from dataclasses import dataclass
from datetime import datetime

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.project_tree_stats import (
    DocumentTreeStats,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.cast import assert_cast


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
            DocumentTreeIterator(
                assert_cast(traceability_index.document_tree, DocumentTree)
            )
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

    def get_datetime(self) -> str:
        return datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    def document_status_have_status(self) -> bool:
        statuses = self.document_tree_stats.requirements_status_breakdown.keys()
        return any(key is not None for key in statuses)
