from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates


class DocumentTreeHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(config, traceability_index: TraceabilityIndex):
        document_tree_iterator = DocumentTreeIterator(
            traceability_index.document_tree
        )

        template = DocumentTreeHTMLGenerator.env.get_template(
            "document_tree/document_tree.jinja.html"
        )
        output = template.render(
            config=config,
            document_tree=traceability_index.document_tree,
            artefact_list=document_tree_iterator.iterator(),
            static_path="_static",
            traceability_index=traceability_index,
        )

        return output
