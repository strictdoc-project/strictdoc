from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class DocumentHTML2PDFGenerator:
    @staticmethod
    def export(  # pylint: disable=too-many-arguments
        project_config: ProjectConfig,
        document: Document,
        traceability_index,
        markup_renderer,
        link_renderer: LinkRenderer,
        standalone: bool,
        html_templates: HTMLTemplates,
    ):
        output = ""

        document_tree_iterator = DocumentTreeIterator(
            traceability_index.document_tree
        )

        template = html_templates.jinja_environment().get_template(
            "screens/document/pdf/index.jinja"
        )

        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            project_config=project_config,
            document=document,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            standalone=standalone,
            document_type=DocumentType.pdf(),
            document_iterator=document_iterator,
            strictdoc_version=__version__,
            document_tree=traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
        )

        return output
