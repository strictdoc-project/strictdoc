import os
from pathlib import Path
from typing import Dict, List

import xlsxwriter
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.utility import xl_cell_to_rowcol_abs

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree


EXCEL_SHEET_NAME = "requierements"
MAX_WIDTH = 75
HEADER_MARGIN = 3
MAX_WIDTH_KEY = "max_width"
COLUMN_HEADER_KEY = "header"
PARENT_COLUMN_HEADER_LABEL = "PARENT"
EXPORT_COLUMNS = [
    {
        "name": "uid",
        "header": "UID",
    },
    # {
    #     "name": "title",
    #     "header": "TITLE",
    # },
    {
        "name": "statement",
        "header": "STATEMENT",
    },
    # {
    #     "name": "rationale",
    #     "header": "RATIONALE",
    # },
    # {
    #     "name": "body",
    #     "header": "BODY",
    # },
]


class ExcelGenerator:
    @staticmethod
    def lookup_refs(document_contents: List) -> Dict[str, int]:
        """Lookups each req position in the list, keeping track of where it will be placed in the excel sheet

        Args:
            document_contents (List): List of potential requierement

        Returns:
            Dict[str, int]: Dict containing the position of each requierement
        """
        refs: Dict[str, int] = {}
        row = 1

        for content_node in document_contents:
            if isinstance(content_node, Requirement):
                if content_node.uid:
                    # we only export the requierements with uid, allowing tracking
                    refs[content_node.uid] = row + 1
                    row += 1

        return refs

    def _init_columns_width() -> int:
        """Init the width of each column based on the definition + return the defaullt width for the parent column

        Returns:
            int: Width of the Parent column
        """
        for column in EXPORT_COLUMNS:
            column[MAX_WIDTH_KEY] = (
                len(column[COLUMN_HEADER_KEY]) + HEADER_MARGIN
            )
        parent_header_len = len(PARENT_COLUMN_HEADER_LABEL) + HEADER_MARGIN

        return parent_header_len

    @staticmethod
    def _set_columns_width(
        workbook: Workbook, worksheet: Worksheet, parent_header_len: int
    ):
        """Set the width of each columns based on the max lenght and the max possible

        Args:
            workbook (Workbook): Excel workbook
            worksheet (Worksheet): Excel worksheet
            parent_header_len (int): Len of the parent column
        """
        cell_format_text_wrap = workbook.add_format()
        cell_format_text_wrap.set_text_wrap()

        for idx, column in enumerate(EXPORT_COLUMNS, start=0):
            if column[MAX_WIDTH_KEY] > MAX_WIDTH:
                worksheet.set_column(idx, idx, MAX_WIDTH, cell_format_text_wrap)
            else:
                worksheet.set_column(idx, idx, column[MAX_WIDTH_KEY])
        worksheet.set_column(
            len(EXPORT_COLUMNS), len(EXPORT_COLUMNS), parent_header_len
        )

    @staticmethod
    def _init_headers() -> List:
        """Init the header list

        Returns:
            List: List of header
        """
        headers: List = []

        for column in EXPORT_COLUMNS:
            headers.append({"header": column[COLUMN_HEADER_KEY]})
        headers.append({"header": PARENT_COLUMN_HEADER_LABEL})

        return headers

    @staticmethod
    def export_tree(
        document_tree: DocumentTree, traceability_index, output_excel_root
    ):
        """Will create and fill one excel file per document, containing requierements with an UID

        Args:
            document_tree (DocumentTree): List of document to export
            traceability_index (Any): traceability)index
            output_excel_root (str): Path of the export
        """
        Path(output_excel_root).mkdir(parents=True, exist_ok=True)

        document: Document
        for document in document_tree.document_list:
            document_out_file = Path(
                output_excel_root,
                f"{document.meta.document_filename_base}.xlsx",
            )

            document_contents = list(
                DocumentCachingIterator(document).all_content()
            )  # not ideal but needed to make the first pass to detect refs

            with xlsxwriter.Workbook(document_out_file) as workbook:
                refs = ExcelGenerator.lookup_refs(document_contents)
                worksheet = workbook.add_worksheet(name=EXCEL_SHEET_NAME)

                parent_header_len = ExcelGenerator._init_columns_width()

                row = 1
                for node in document_contents:
                    if not node.is_requirement or not node.uid:
                        # we only export the requierements with uid, allowing tracking
                        continue

                    for idx, column in enumerate(EXPORT_COLUMNS, start=0):
                        if hasattr(node, column["name"]):
                            if column["name"] == "statement":
                                value = node.get_statement_single_or_multiline()
                            elif column["name"] == "rationale":
                                value = node.get_rationale_single_or_multiline()
                            else:
                                value = getattr(node, column["name"])
                            worksheet.write(row, idx, value)
                            if value and len(value) > column[MAX_WIDTH_KEY]:
                                column[MAX_WIDTH_KEY] = len(value)

                    if node.references:
                        ref = node.references[0]
                        if len(ref.path) > parent_header_len:
                            parent_header_len = len(ref.path)
                        worksheet.write_url(
                            row,
                            len(EXPORT_COLUMNS),
                            f"internal:'{EXCEL_SHEET_NAME}'!A{refs[ref.path]}",
                            string=ref.path,
                        )
                    row += 1

                # we add a table around all this data, allowing filtering and ordering in Excel
                worksheet.add_table(
                    0,
                    0,
                    row - 1,
                    len(EXPORT_COLUMNS),
                    {"columns": ExcelGenerator._init_headers()},
                )

                # we enforce columns width
                ExcelGenerator._set_columns_width(
                    workbook, worksheet, parent_header_len
                )
