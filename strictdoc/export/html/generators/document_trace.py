from jinja2 import Environment, PackageLoader

from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class DocumentTraceHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document, traceability_index, link_renderer):
        output = ""

        markup_renderer = MarkupRenderer()

        template = DocumentTraceHTMLGenerator.env.get_template(
            "single_document_traceability/document.jinja.html"
        )

        output += template.render(
            document=document,
            traceability_index=traceability_index,
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document_type=DocumentType.trace(),
        )

        return output
