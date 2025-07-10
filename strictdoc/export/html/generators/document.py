"""
@relation(SDOC-SRS-54, scope=file)
"""

from markupsafe import Markup

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.git_client import GitClient


class DocumentHTMLGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
        markup_renderer: MarkupRenderer,
        link_renderer: LinkRenderer,
        git_client: GitClient,
        standalone: bool,
        html_templates: HTMLTemplates,
    ) -> Markup:
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.DOCUMENT,
            document=document,
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            git_client=git_client,
            standalone=standalone,
        )
        return view_object.render_screen(html_templates.jinja_environment())
