# mypy: disable-error-code="arg-type,no-untyped-def,type-arg,union-attr,var-annotated"
import os
from pathlib import Path
from typing import Dict, List

import xlsxwriter
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import (
    FileReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.type_system import ReferenceType
from strictdoc.core.project_config import ProjectConfig
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
    {
        "name": "statement",
        "header": "STATEMENT",
    },
]


class ExcelGenerator:
    @staticmethod
    def export_tree(
        traceability_index: TraceabilityIndex,
        output_excel_root: str,
        project_config: ProjectConfig,
    ):
        Path(output_excel_root).mkdir(parents=True, exist_ok=True)

        document: SDocDocument
        for document in traceability_index.document_tree.document_list:
            document_out_file_name = (
                f"{document.meta.document_filename_base}.xlsx"
            )
            document_out_file = os.path.join(
                output_excel_root, document_out_file_name
            )

            ExcelGenerator._export_single_document(
                document, traceability_index, document_out_file, project_config
            )

    @staticmethod
    def _export_single_document(
        document: SDocDocument,
        traceability_index,
        document_out_file,
        project_config: ProjectConfig,
    ):
        with xlsxwriter.Workbook(document_out_file) as workbook:
            worksheet = workbook.add_worksheet(name=EXCEL_SHEET_NAME)
            workbook.set_properties(
                {
                    "title": project_config.project_title,
                    "comments": "Created with StrictDoc.",
                }
            )

            row = 1  # Header-Row
            fields = project_config.excel_export_fields
            # TODO: Check if all fields are defined by the DocumentGrammar
            columns = ExcelGenerator._init_columns_width(fields)

            req_uid_rows = ExcelGenerator._lookup_refs(
                traceability_index.get_document_iterator(document).all_content(
                    print_fragments=False, print_fragments_from_files=False
                )
            )

            if len(req_uid_rows):
                for node in traceability_index.get_document_iterator(
                    document
                ).all_content(
                    print_fragments=False, print_fragments_from_files=False
                ):
                    if not node.is_requirement or not node.reserved_uid:
                        # only export the requirements with uid
                        continue

                    for idx, field in enumerate(fields, start=0):
                        field_uc = field.upper()

                        # Special treatment for ParentReqReference and Comments
                        if field_uc in (
                            "RELATIONS:PARENT",
                            "PARENT",
                            "PARENTS",
                        ):
                            parent_refs = node.get_requirement_references(
                                ReferenceType.PARENT
                            )
                            if len(parent_refs) > 0:
                                # TODO Allow multiple parent refs
                                ref = parent_refs[0]
                                columns[field][MAX_WIDTH_KEY] = max(
                                    len(ref.ref_uid),
                                    columns[field][MAX_WIDTH_KEY],
                                )
                                if ref.ref_uid in req_uid_rows:
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
                                else:
                                    worksheet.write(row, idx, ref.ref_uid)
                        elif field_uc in ("COMMENT", "COMMENTS"):
                            # Using a transition marker to separate multiple
                            # comments
                            comment_fields = node.get_comment_fields()
                            if len(comment_fields) > 0:
                                comment_row_value: str = ""
                                for comment_field_ in comment_fields:
                                    if len(comment_row_value) > 0:
                                        comment_row_value += "\n----------\n"
                                    comment_row_value += (
                                        comment_field_.get_text_value()
                                    )
                                worksheet.write(row, idx, comment_row_value)
                                if (
                                    comment_row_value
                                    and len(comment_row_value)
                                    > columns[field][MAX_WIDTH_KEY]
                                ):
                                    columns[field][MAX_WIDTH_KEY] = len(
                                        comment_row_value
                                    )
                        elif field_uc == "RELATIONS":
                            if len(node.relations) > 0:
                                relations_components = []
                                # Using a transition marker to separate
                                # multiple references
                                for ref in node.relations:
                                    if isinstance(ref, ParentReqReference):
                                        relations_components.append(
                                            ref.ref_type + ": " + ref.ref_uid
                                        )
                                    elif isinstance(ref, FileReference):
                                        relations_components.append(
                                            ref.ref_type
                                            + ": "
                                            + ref.get_posix_path()
                                        )
                                relations_row_value: str = (
                                    "\n----------\n".join(relations_components)
                                )
                                worksheet.write(row, idx, relations_row_value)
                                value_len = len(relations_row_value)
                                columns[field][MAX_WIDTH_KEY] = max(
                                    value_len, columns[field][MAX_WIDTH_KEY]
                                )
                        elif field_uc in node.ordered_fields_lookup.keys():
                            req_field = node.ordered_fields_lookup[field_uc][0]
                            value: str = req_field.get_text_value()
                            worksheet.write(row, idx, value)
                            value_len = len(value)
                            columns[field][MAX_WIDTH_KEY] = max(
                                value_len, columns[field][MAX_WIDTH_KEY]
                            )
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
                print(  # noqa: T201
                    "No requirement with UID, nothing to export into excel"
                )

        if row == 1:
            os.unlink(document_out_file)

    @staticmethod
    def _lookup_refs(document_contents: List) -> Dict[str, int]:
        refs: Dict[str, int] = {}
        row = 1

        for content_node in document_contents:
            if isinstance(content_node, SDocNode):
                if content_node.reserved_uid:
                    # only export the requirements with uid, allowing tracking
                    row += 1
                    refs[content_node.reserved_uid] = row

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
