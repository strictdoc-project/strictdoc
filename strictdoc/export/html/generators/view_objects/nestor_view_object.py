# pragma: no cover file
from dataclasses import dataclass
from typing import Optional

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates, JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.cast import assert_cast


@dataclass
class NestorViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        templates: HTMLTemplates,
        path_to_json: str,
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.templates: HTMLTemplates = templates
        self.path_to_json: str = path_to_json

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        markup_renderer = MarkupRenderer.create(
            "RST",
            traceability_index,
            link_renderer,
            templates,
            project_config,
            None,
        )

        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.standalone: bool = False
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(
                assert_cast(traceability_index.document_tree, DocumentTree)
            )
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__
        self.current_view = DocumentView.create_default(None).views[0]
        self.document_type: DocumentType = DocumentType.DOCUMENT
        self.link_document_type: DocumentType = DocumentType.DOCUMENT
        self.document: Optional[SDocDocument] = None

    def render_screen(self, jinja_environment: JinjaEnvironment) -> str:
        return jinja_environment.render_template_as_markup(
            "screens/nestor/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)
