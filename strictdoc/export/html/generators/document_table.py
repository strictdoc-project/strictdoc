from jinja2 import Environment, PackageLoader, StrictUndefined

from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class DocumentTableHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        undefined=StrictUndefined,
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document, traceability_index, link_renderer):
        output = ""

        markup_renderer = MarkupRenderer()

        template = DocumentTableHTMLGenerator.env.get_template(
            "single_document_table/document.jinja.html"
        )

        root_path = document.meta.get_root_path_prefix()
        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            document=document,
            traceability_index=traceability_index,
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document_type=DocumentType.table(),
            standalone=False,
            root_path=root_path,
            document_iterator=document_iterator,
        )

        return output
