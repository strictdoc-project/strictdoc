from jinja2 import Environment, PackageLoader, StrictUndefined

from strictdoc.export.html.document_type import DocumentType


class DocumentTableHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        undefined=StrictUndefined,
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(
        config, document, traceability_index, markup_renderer, link_renderer
    ):
        output = ""

        template = DocumentTableHTMLGenerator.env.get_template(
            "single_document_table/document.jinja.html"
        )

        root_path = document.meta.get_root_path_prefix()
        static_path = f"{root_path}/_static"
        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            config=config,
            document=document,
            traceability_index=traceability_index,
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document_type=DocumentType.table(),
            standalone=False,
            root_path=root_path,
            static_path=static_path,
            document_iterator=document_iterator,
        )

        return output
