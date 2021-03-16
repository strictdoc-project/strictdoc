from jinja2 import Environment, PackageLoader

from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class DocumentHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates")
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(
        document_tree,
        document,
        traceability_index,
        link_renderer,
        standalone=False,
    ):
        output = ""

        markup_renderer = MarkupRenderer()

        template = DocumentHTMLGenerator.env.get_template(
            "single_document/document.jinja.html"
        )

        output += template.render(
            document=document,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            standalone=standalone,
            document_type=DocumentType.document(),
        )

        return output
