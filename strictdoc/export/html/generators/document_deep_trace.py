from jinja2 import Environment, PackageLoader

from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class DocumentDeepTraceHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export_deep(document, traceability_index, link_renderer):
        output = ""

        markup_renderer = MarkupRenderer()

        template = DocumentDeepTraceHTMLGenerator.env.get_template(
            "single_document_traceability_deep/document.jinja.html"
        )

        output += template.render(
            document=document,
            traceability_index=traceability_index,
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document_type=DocumentType.deeptrace(),
        )

        return output
