from jinja2 import Environment, PackageLoader

from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.export.html.export import get_traceability_link, get_traceability_deep_link


class DocumentTreeHTMLExport:
    OFFSET = 8

    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates')
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree):
        document_tree_iterator = DocumentTreeIterator(document_tree)

        template = DocumentTreeHTMLExport.env.get_template('document_tree/document_tree.jinja.html')
        output = template.render(document_tree=document_tree,
                                 artefact_list=document_tree_iterator.iterator(),
                                 get_traceability_link=get_traceability_link,
                                 get_traceability_deep_link=get_traceability_deep_link)

        return output
