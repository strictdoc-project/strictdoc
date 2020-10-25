import os

from strictdoc.export.rst.writer import RSTWriter


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


class SingleDocumentRSTExport:
    @staticmethod
    def export(document_tree, document, traceability_index):
        writer = RSTWriter()

        output = writer.write(document)

        return output
