# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.git_client import GitClient


class DocumentTableHTMLGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        document,
        traceability_index,
        markup_renderer,
        link_renderer: LinkRenderer,
        git_client: GitClient,
        html_templates: HTMLTemplates,
    ):
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.table(),
            document=document,
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            git_client=git_client,
            standalone=False,
        )
        return view_object.render_screen(html_templates.jinja_environment())
