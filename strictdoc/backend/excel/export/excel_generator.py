import os
from pathlib import Path
from typing import Dict, List

import xlsxwriter
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.reference import (
    ParentReqReference,
    FileReference,
    BibReference,
)
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.type_system import ReferenceType
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.traceability_index import TraceabilityIndex

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
        traceability_index: TraceabilityIndex,
        output_excel_root: str,
        config: ExportCommandConfig,
    ):
        Path(output_excel_root).mkdir(parents=True, exist_ok=True)

        document: Document
        for document in traceability_index.document_tree.document_list:
            document_out_file_name = (
                f"{document.meta.document_filename_base}.xlsx"
            )
            document_out_file = os.path.join(
                output_excel_root, document_out_file_name
            )

            ExcelGenerator._export_single_document(
                document, traceability_index, document_out_file, config
            )

    @staticmethod
    def _export_single_document(
        document: Document,
        traceability_index,
        document_out_file,
        config,
    ):
        with xlsxwriter.Workbook(document_out_file) as workbook:
            worksheet = workbook.add_worksheet(name=EXCEL_SHEET_NAME)
            workbook.set_properties(
                {
                    "title": config.project_title,
                    "comments": "Created with StrictDoc",
                }
            )

            row = 1  # Header-Row
            fields = config.fields
            # TODO: Check if all fields are defined by the DocumentGrammar
            columns = ExcelGenerator._init_columns_width(fields)

            req_uid_rows = ExcelGenerator._lookup_refs(
                traceability_index.get_document_iterator(document).all_content()
            )

            if len(req_uid_rows):
                for node in traceability_index.get_document_iterator(
                    document
                ).all_content():
                    if not node.is_requirement or not node.uid:
                        # only export the requirements with uid
                        continue

                    for idx, field in enumerate(fields, start=0):
                        field_uc = field.upper()

                        # Special treatment for ParentReqReference and Comments
                        if field_uc in ("REFS:PARENT", "PARENT", "PARENTS"):
                            parent_refs = node.get_requirement_references(
                                ReferenceType.PARENT
                            )
                            if len(parent_refs) > 0:
                                # TODO Allow multiple parent refs
                                ref = parent_refs[0]
                                if (
                                    len(ref.ref_uid)
                                    > columns[field][MAX_WIDTH_KEY]
                                ):
                                    columns[field][MAX_WIDTH_KEY] = len(
                                        ref.ref_uid
                                    )
                                worksheet.write_url(
                                    row,
                                    idx,
                                    (
                                        "internal:"
                                        f"'{EXCEL_SHEET_NAME}'"
                                        f"!A{req_uid_rows[ref.ref_uid]}"
                                    ),
                                    string=ref.ref_uid,
                                )
                        elif field_uc in ("COMMENT", "COMMENTS"):
                            # Using a transition marker to separate multiple
                            # comments
                            if node.comments:
                                value = ""
                                for comment in node.comments:
                                    if len(value) > 0:
                                        value += "\n----------\n"
                                    value += comment.get_comment()
                                worksheet.write(row, idx, value)
                                if (
                                    value
                                    and len(value)
                                    > columns[field][MAX_WIDTH_KEY]
                                ):
                                    columns[field][MAX_WIDTH_KEY] = len(value)
                        elif field_uc in node.ordered_fields_lookup.keys():
                            req_field = node.ordered_fields_lookup[field_uc][0]
                            value = ""
                            if req_field.field_value_references:
                                # Using a transition marker to separate
                                # multiple references
                                for ref in req_field.field_value_references:
                                    if len(value) > 0:
                                        value += "----------\n"
                                    if isinstance(ref, ParentReqReference):
                                        value += (
                                            ref.ref_type
                                            + ": "
                                            + ref.ref_uid
                                            + "\n"
                                        )
                                    elif isinstance(ref, FileReference):
                                        value += (
                                            ref.ref_type
                                            + ": "
                                            + ref.file_entry.file_path
                                            + "\n"
                                        )
                                    elif isinstance(ref, BibReference):
                                        value += (
                                            ref.ref_type
                                            + ": "
                                            + ref.bib_entry.bib_value
                                            + "\n"
                                        )
                            else:
                                value = req_field.get_value()
                            worksheet.write(row, idx, value)
                            vallength = len(value)
                            if vallength > columns[field][MAX_WIDTH_KEY]:
                                columns[field][MAX_WIDTH_KEY] = vallength
                        elif hasattr(node, "special_fields"):
                            if len(node.special_fields):
                                for special_field in node.special_fields:
                                    if (
                                        special_field.field_name.upper()
                                        == field_uc
                                    ):
                                        value = special_field.field_value
                                        worksheet.write(row, idx, value)
                                        if (
                                            value
                                            and len(value)
                                            > columns[field][MAX_WIDTH_KEY]
                                        ):
                                            columns[field][MAX_WIDTH_KEY] = len(
                                                value
                                            )
                                        break

                    row += 1

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
            else:
                # no requirement with UID
                print("No requirement with UID, nothing to export into excel")

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
                    row += 1
                    refs[content_node.uid] = row

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
