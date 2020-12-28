import os
from pathlib import Path

from strictdoc.core.document_tree import DocumentTree
from strictdoc.export.rst.writer import RSTWriter


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


class DocumentRSTGenerator:
    @staticmethod
    def export_tree(
        document_tree: DocumentTree, traceability_index, output_rst_root
    ):
        Path(output_rst_root).mkdir(parents=True, exist_ok=True)
        for document in document_tree.document_list:
            document_content = DocumentRSTGenerator.export(
                document_tree, document, traceability_index
            )

            document_out_file = "{}/{}.rst".format(
                output_rst_root, document.name
            )
            with open(document_out_file, "w") as file:
                file.write(document_content)

    @staticmethod
    def export(document_tree: DocumentTree, document, traceability_index):
        writer = RSTWriter(traceability_index)

        single_or_many = len(document_tree.document_list) == 1
        output = writer.write(document, single_or_many)

        return output
