# mypy: disable-error-code="no-untyped-call"
import urllib
from dataclasses import dataclass
from typing import List, Optional, Set

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.git.change_generator import ChangeContainer
from strictdoc.git.project_diff_analyzer import (
    ChangeStats,
    ProjectTreeDiffStats,
)
from strictdoc.helpers.cast import assert_cast


@dataclass
class DiffScreenResultsViewObject:
    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        change_container: ChangeContainer,
        document_tree_lhs: DocumentTree,
        document_tree_rhs: DocumentTree,
        documents_iterator_lhs: DocumentTreeIterator,
        documents_iterator_rhs: DocumentTreeIterator,
        left_revision: Optional[str],
        right_revision: Optional[str],
        lhs_stats: ProjectTreeDiffStats,
        rhs_stats: ProjectTreeDiffStats,
        change_stats: ChangeStats,
        traceability_index_lhs: TraceabilityIndex,
        traceability_index_rhs: TraceabilityIndex,
        tab: str,
    ):
        self.project_config: ProjectConfig = project_config
        self.change_container: ChangeContainer = change_container
        self.document_tree_lhs: DocumentTree = document_tree_lhs
        self.document_tree_rhs: DocumentTree = document_tree_rhs
        self.documents_iterator_lhs = documents_iterator_lhs
        self.documents_iterator_rhs = documents_iterator_rhs
        self.left_revision: Optional[str] = left_revision
        self.right_revision: Optional[str] = right_revision
        self.lhs_stats = lhs_stats
        self.rhs_stats = rhs_stats
        self.change_stats = change_stats
        self.traceability_index_lhs: TraceabilityIndex = traceability_index_lhs
        self.traceability_index_rhs: TraceabilityIndex = traceability_index_rhs
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

    @property
    def left_revision_urlencoded(self) -> str:
        return (
            urllib.parse.quote(self.left_revision)
            if self.left_revision is not None
            else ""
        )

    @property
    def right_revision_urlencoded(self) -> str:
        return (
            urllib.parse.quote(self.right_revision)
            if self.right_revision is not None
            else ""
        )

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/git/index.jinja", view_object=self
        )

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)

    def get_node_types(self) -> List[str]:
        node_types: Set[str] = set()

        document_: SDocDocument
        for document_ in self.document_tree_lhs.document_list:
            document_grammar = assert_cast(document_.grammar, DocumentGrammar)

            for node_type_ in document_grammar.elements_by_type.keys():
                node_types.add(node_type_)

        for document_ in self.document_tree_rhs.document_list:
            document_grammar = assert_cast(document_.grammar, DocumentGrammar)

            for node_type_ in document_grammar.elements_by_type.keys():
                node_types.add(node_type_)

        priority_order = {"SECTION": 0, "TEXT": 1, "REQUIREMENT": 2}
        return sorted(node_types, key=lambda x: (priority_order.get(x, 100), x))

    def should_display_old_section_as_deprecated(self) -> bool:
        return self.project_config.is_new_section_behavior()
