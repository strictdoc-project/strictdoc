# mypy: disable-error-code="attr-defined,no-any-return,no-untyped-call,no-untyped-def"
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.git.change_generator import ChangeContainer


@dataclass
class DiffScreenResultsViewObject:
    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        change_container: ChangeContainer,
        document_tree_lhs,
        document_tree_rhs,
        documents_iterator_lhs,
        documents_iterator_rhs,
        left_revision: str,
        left_revision_urlencoded: str,
        right_revision: str,
        right_revision_urlencoded: str,
        lhs_stats,
        rhs_stats,
        change_stats,
        traceability_index_lhs,
        traceability_index_rhs,
        tab: str,
    ):
        self.project_config: ProjectConfig = project_config
        self.change_container: ChangeContainer = change_container
        self.document_tree_lhs = document_tree_lhs
        self.document_tree_rhs = document_tree_rhs
        self.documents_iterator_lhs = documents_iterator_lhs
        self.documents_iterator_rhs = documents_iterator_rhs
        self.left_revision: str = left_revision
        self.left_revision_urlencoded: str = left_revision_urlencoded
        self.right_revision: str = right_revision
        self.right_revision_urlencoded: str = right_revision_urlencoded
        self.lhs_stats = lhs_stats
        self.rhs_stats = rhs_stats
        self.change_stats = change_stats
        self.traceability_index_lhs = traceability_index_lhs
        self.traceability_index_rhs = traceability_index_rhs
        self.tab: str = tab
        self.results: bool = True
        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.link_renderer: LinkRenderer = link_renderer
        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__
        self.error_message: Optional[str] = None

    def render_screen(self, jinja_environment: JinjaEnvironment):
        template = jinja_environment.environment.overlay(
            autoescape=False
        ).get_template("screens/git/index.jinja")
        return template.render(view_object=self)

    def render_url(self, url: str):
        return self.link_renderer.render_url(url)

    def render_node_link(self, incoming_link, document, document_type):
        return self.link_renderer.render_node_link(
            incoming_link, document, document_type
        )

    def render_static_url(self, url: str):
        return self.link_renderer.render_static_url(url)

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)

    def render_local_anchor(self, node):
        return self.link_renderer.render_local_anchor(node)

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def date_today(self):
        return datetime.today().strftime("%Y-%m-%d")
