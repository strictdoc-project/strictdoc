# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def,union-attr"
from typing import List, Optional, Tuple

from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class TraceabilityMatrixViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        link_renderer: LinkRenderer,
        markup_renderer: MarkupRenderer,
        known_relations_list: List[Tuple[str, Optional[str]]],
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.known_relations_list: List[Tuple[str, Optional[str]]] = (
            known_relations_list
        )
        self.standalone: bool = False
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(traceability_index.document_tree)
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def iterate_documents(self):
        yield from filter(
            lambda document_: not document_.document_is_included(),
            self.traceability_index.document_tree.document_list,
        )

    def render_screen(self, jinja_environment: JinjaEnvironment):
        return jinja_environment.render_template_as_markup(
            "screens/traceability_matrix/index.jinja", view_object=self
        )

    def render_static_url(self, url: str):
        return self.link_renderer.render_static_url(url)

    def render_url(self, url: str):
        return self.link_renderer.render_url(url)

    def render_local_anchor(self, node):
        return self.link_renderer.render_local_anchor(node)
