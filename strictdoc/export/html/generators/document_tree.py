from jinja2 import Environment, PackageLoader, StrictUndefined

from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.traceability_index import TraceabilityIndex


class DocumentTreeHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        undefined=StrictUndefined,
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(config, document_tree, traceability_index: TraceabilityIndex):
        document_tree_iterator = DocumentTreeIterator(document_tree)

        template = DocumentTreeHTMLGenerator.env.get_template(
            "document_tree/document_tree.jinja.html"
        )
        output = template.render(
            config=config,
            document_tree=document_tree,
            artefact_list=document_tree_iterator.iterator(),
            static_path="_static",
            traceability_index=traceability_index,
        )

        return output
