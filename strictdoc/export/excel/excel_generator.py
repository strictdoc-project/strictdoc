import os
from pathlib import Path
from typing import Dict, List

import xlsxwriter
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.core.document_tree import DocumentTree

EXCEL_SHEET_NAME = "Requirements"
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
]


class ExcelGenerator:
    @staticmethod
    def export_tree(
        document_tree: DocumentTree,
        traceability_index,
        output_excel_root,
        fields: List[str],
    ):
        Path(output_excel_root).mkdir(parents=True, exist_ok=True)

        document: Document
        for document in document_tree.document_list:
            document_out_file_name = (
                f"{document.meta.document_filename_base}.xlsx"
            )
            document_out_file = os.path.join(
                output_excel_root, document_out_file_name
            )

            ExcelGenerator._export_single_document(
                document, traceability_index, document_out_file, fields
            )

    @staticmethod
    def _export_single_document(
        document: Document,
        traceability_index,
        document_out_file,
        fields: List[str],
    ):
        with xlsxwriter.Workbook(document_out_file) as workbook:
            refs = ExcelGenerator._lookup_refs(
                traceability_index.get_document_iterator(document).all_content()
            )
            worksheet = workbook.add_worksheet(name=EXCEL_SHEET_NAME)

            columns = ExcelGenerator._init_columns_width(fields)

            row = 1
            for node in traceability_index.get_document_iterator(
                document
            ).all_content():
                if not node.is_requirement or not node.uid:
                    # only export the requirements with uid, allowing tracking
                    continue

                for idx, field in enumerate(fields, start=0):
                    if field == "parent":
                        if node.references:
                            ref = node.references[0]
                            if len(ref.path) > columns[field][MAX_WIDTH_KEY]:
                                columns[field][MAX_WIDTH_KEY] = len(ref.path)
                            worksheet.write_url(
                                row,
                                idx,
                                (
                                    "internal:"
                                    f"'{EXCEL_SHEET_NAME}'!A{refs[ref.path]}"
                                ),
                                string=ref.path,
                            )
                    elif hasattr(node, field):
                        if field == "statement":
                            value = node.get_statement_single_or_multiline()
                        elif field == "rationale":
                            value = node.get_rationale_single_or_multiline()
                        elif field == "comments":
                            # TODO: how do we want to join multiple comment?
                            # I am using only one comment with multi line
                            if len(node.comments):
                                value = node.comments[0].get_comment()
                            else:
                                value = ""
                        else:
                            value = getattr(node, field)
                        worksheet.write(row, idx, value)
                        if value and len(value) > columns[field][MAX_WIDTH_KEY]:
                            columns[field][MAX_WIDTH_KEY] = len(value)
                    elif len(node.special_fields):
                        for special_field in node.special_fields:
                            if special_field.field_name.lower() == field:
                                value = special_field.field_value
                                worksheet.write(row, idx, value)
                                if (
                                    value
                                    and len(value)
                                    > columns[field][MAX_WIDTH_KEY]
                                ):
                                    columns[field][MAX_WIDTH_KEY] = len(value)
                                break
                row += 1

            if row == 1:
                # no requirement with UID
                print("No requirement with UID, nothing to export into excel")
            else:
                # add a table around all this data, allowing filtering and
                # ordering in Excel
                worksheet.add_table(
                    0,
                    0,
                    row - 1,
                    len(fields) - 1,
                    {"columns": ExcelGenerator._init_headers(fields)},
                )

                # enforce columns width
                ExcelGenerator._set_columns_width(
                    workbook, worksheet, columns, fields
                )

        if row == 1:
            os.unlink(document_out_file)

    @staticmethod
    def _lookup_refs(document_contents: List) -> Dict[str, int]:
        refs: Dict[str, int] = {}
        row = 1

        for content_node in document_contents:
            if isinstance(content_node, Requirement):
                if content_node.uid:
                    # only export the requirements with uid, allowing tracking
                    refs[content_node.uid] = row + 1
                    row += 1

        return refs

    @staticmethod
    def _init_columns_width(fields: List[str]):
        columns = {}

        for field in fields:
            columns[field] = {}
            columns[field][MAX_WIDTH_KEY] = len(field) + HEADER_MARGIN
        return columns

    @staticmethod
    def _set_columns_width(
        workbook: Workbook, worksheet: Worksheet, columns, fields: List[str]
    ):
        cell_format_text_wrap = workbook.add_format()
        cell_format_text_wrap.set_text_wrap()

        for idx, field in enumerate(fields, start=0):
            if columns[field][MAX_WIDTH_KEY] > MAX_WIDTH:
                worksheet.set_column(idx, idx, MAX_WIDTH, cell_format_text_wrap)
            else:
                worksheet.set_column(idx, idx, columns[field][MAX_WIDTH_KEY])

    @staticmethod
    def _init_headers(fields: List[str]) -> List:
        headers: List = []

        for field in fields:
            headers.append({"header": field.upper()})

        return headers
