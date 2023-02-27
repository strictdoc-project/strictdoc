from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class DocumentHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(  # pylint: disable=too-many-arguments
        config,
        document: Document,
        traceability_index,
        markup_renderer,
        link_renderer: LinkRenderer,
        standalone: bool,
    ):
        output = ""

        template = DocumentHTMLGenerator.env.get_template(
            "single_document/document.jinja.html"
        )

        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            config=config,
            document=document,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            standalone=standalone,
            document_type=DocumentType.document(),
            document_iterator=document_iterator,
            strictdoc_version=__version__,
        )

        return output
