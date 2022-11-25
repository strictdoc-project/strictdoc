from strictdoc.backend.sdoc.models.document import Document
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates


class DocumentHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(  # pylint: disable=too-many-arguments
        config,
        document: Document,
        traceability_index,
        markup_renderer,
        link_renderer,
        standalone: bool,
    ):
        output = ""

        template = DocumentHTMLGenerator.env.get_template(
            "single_document/document.jinja.html"
        )

        root_path = document.meta.get_root_path_prefix()
        static_path = f"{root_path}/_static"
        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            config=config,
            document=document,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            standalone=standalone,
            document_type=DocumentType.document(),
            root_path=root_path,
            static_path=static_path,
            document_iterator=document_iterator,
        )

        return output
