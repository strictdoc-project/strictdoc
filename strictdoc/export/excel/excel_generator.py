import os
from pathlib import Path

import xlsxwriter

from strictdoc.backend.dsl.models.document import Document
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


class ExcelGenerator:
    @staticmethod
    def export_tree(
        document_tree: DocumentTree, traceability_index, output_excel_root
    ):
        Path(output_excel_root).mkdir(parents=True, exist_ok=True)

        document: Document
        for document in document_tree.document_list:
            document_out_file = "{}/{}.xlsx".format(
                output_excel_root, document.meta.document_filename_base
            )

            workbook = xlsxwriter.Workbook(document_out_file)
            worksheet = workbook.add_worksheet()

            style_bold = workbook.add_format({'bold': True})

            for header_idx, header in enumerate([
                'UID',
                'TITLE',
                'STATEMENT',
                'RATIONALE'
            ]):
                worksheet.write(0, header_idx, header, style_bold)

            iterator = DocumentCachingIterator(document)
            for node_idx, node in enumerate(iterator.all_content()):
                row = node_idx + 2
                if not node.is_requirement:
                    continue

                worksheet.write(row, 0, node.uid)
                worksheet.write(row, 1, node.title)

                statement = node.get_statement_single_or_multiline()
                if statement:
                    worksheet.write(row, 2, statement)

                rationale = node.get_rationale_single_or_multiline()
                if rationale:
                    worksheet.write(row, 3, rationale)

            workbook.close()
