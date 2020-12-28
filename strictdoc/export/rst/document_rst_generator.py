import os

from strictdoc.core.document_tree import DocumentTree
from strictdoc.export.rst.writer import RSTWriter


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


class DocumentRSTGenerator:
    @staticmethod
    def export(document_tree: DocumentTree, document, traceability_index):
        writer = RSTWriter(traceability_index)

        single_or_many = len(document_tree.document_list) == 1
        output = writer.write(document, single_or_many)

        return output
