from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class DocumentTraceHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(
        config,
        document,
        traceability_index,
        markup_renderer,
        link_renderer: LinkRenderer,
    ):
        output = ""

        template = DocumentTraceHTMLGenerator.env.get_template(
            "single_document_traceability/document.jinja.html"
        )

        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            config=config,
            document=document,
            traceability_index=traceability_index,
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document_type=DocumentType.trace(),
            standalone=False,
            document_iterator=document_iterator,
        )

        return output
