import os
from typing import Optional, NamedTuple, List

import xlrd

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import Reference
from strictdoc.backend.sdoc.models.requirement import (
    RequirementField,
    Requirement,
)
from strictdoc.backend.sdoc.models.type_system import GrammarElementFieldString


class RequirementColumns(NamedTuple):
    uid_column: Optional[int]
    title_column: Optional[int]
    statement_column: Optional[int]
    comment_column: Optional[int]
    parent_column: Optional[int]
    extra_header_pairs: List


# pylint: disable=too-many-instance-attributes
class ExcelToSDocConverter:
    @staticmethod
    def lookup_header_row_num(first_sheet):
        for i in range(16):  # the first 16 rows should do ¯\_(ツ)_/¯
            if first_sheet.row_values(0)[0].strip() != "":
                return i
        return None

    @staticmethod
    def get_safe_header_row(first_sheet, header_row_num):
        def safe_name(dangerous_name):
            dangerous_name = dangerous_name.splitlines()[0]
            dangerous_name = dangerous_name.strip()
            dangerous_name = dangerous_name.upper()
            dangerous_name = dangerous_name.replace(":", "")
            dangerous_name = dangerous_name.replace("+", "")
            dangerous_name = dangerous_name.replace(",", "_")
            dangerous_name = dangerous_name.replace(" ", "_")
            dangerous_name = dangerous_name.replace("-", "_")
            dangerous_name = dangerous_name.replace("/", "_OR_")
            return dangerous_name

        header_row = first_sheet.row_values(header_row_num)
        header_row = list(safe_name(x) for x in header_row)
        return header_row

    @staticmethod
    def get_any_header_column(first_sheet, header_texts, header_row_num):
        if not isinstance(header_texts, list):
            header_texts = [header_texts]
        for text in header_texts:
            try:
                return ExcelToSDocConverter.get_safe_header_row(
                    first_sheet, header_row_num
                ).index(text)
            except ValueError:
                continue
        return None

    @staticmethod
    def convert(excel_file) -> Document:
        excel_workbook = xlrd.open_workbook(filename=excel_file, on_demand=True)
        first_sheet = excel_workbook.sheet_by_index(0)

        # Find a row that is a header row with field titles.
        header_row_num = ExcelToSDocConverter.lookup_header_row_num(first_sheet)
        assert header_row_num is not None

        excel_file_name = os.path.basename(excel_file)
        title = excel_file_name + " sheet " + first_sheet.name

        # Identify all columns
        all_header_columns = list(range(first_sheet.ncols))

        statement_column = ExcelToSDocConverter.get_any_header_column(
            first_sheet, ["REQUIREMENT", "STATEMENT"], header_row_num
        )
        if statement_column is not None:
            all_header_columns.remove(statement_column)
        uid_column = ExcelToSDocConverter.get_any_header_column(
            first_sheet,
            ["REF", "REF #", "REF_#", "REFDES", "ID", "UID"],
            header_row_num,
        )
        if uid_column is not None:
            all_header_columns.remove(uid_column)
        comment_column = ExcelToSDocConverter.get_any_header_column(
            first_sheet, ["REMARKS", "COMMENT"], header_row_num
        )
        if comment_column is not None:
            all_header_columns.remove(comment_column)
        title_column = ExcelToSDocConverter.get_any_header_column(
            first_sheet, ["TITLE", "NAME"], header_row_num
        )
        if title_column is not None:
            all_header_columns.remove(title_column)
        parent_column = ExcelToSDocConverter.get_any_header_column(
            first_sheet, ["PARENT", "PARENT_REF", "PARENT_UID"], header_row_num
        )
        if parent_column is not None:
            all_header_columns.remove(parent_column)

        header_row = ExcelToSDocConverter.get_safe_header_row(
            first_sheet, header_row_num
        )
        # [(0, 'APPLICABLE_COMPONENT_CATEGORIES'),
        # (2, 'CATEGORY'),
        # (4, 'PUBLIC_REQUIREMENTS_REFERENCES_OR_DESCRIPTIONS'),
        # (5, 'VERIFICATION_INSPECTION__DEMONSTRATION__TEST__OR_ANALYSIS'),
        # (6, 'CRITICALITY')]
        extra_header_pairs = list(
            map(lambda x: (x, header_row[x]), all_header_columns)
        )
        columns = RequirementColumns(
            uid_column=uid_column,
            title_column=title_column,
            statement_column=statement_column,
            comment_column=comment_column,
            parent_column=parent_column,
            extra_header_pairs=extra_header_pairs,
        )

        # validate_all_required_columns
        assert columns.statement_column is not None

        document = ExcelToSDocConverter.create_document(
            title, extra_header_pairs
        )
        for i in range(header_row_num + 1, first_sheet.nrows):
            requirement = ExcelToSDocConverter.create_requirement(
                first_sheet, document, i, columns
            )
            document.section_contents.append(requirement)

        return document

    @staticmethod
    def create_document(title: Optional[str], extra_header_pairs) -> Document:
        document_config = DocumentConfig(
            parent=None,
            version=None,
            number=None,
            markup=None,
            auto_levels=None,
        )
        document_title = title if title else "<No title>"
        document = Document(None, document_title, document_config, None, [], [])

        fields = DocumentGrammar.create_default(document).elements[0].fields
        for _, name in extra_header_pairs:
            fields.extend(
                [
                    GrammarElementFieldString(
                        parent=None, title=name, required="False"
                    ),
                ]
            )

        requirements_element = GrammarElement(
            parent=None, tag="REQUIREMENT", fields=fields
        )
        elements = [requirements_element]
        grammar = DocumentGrammar(parent=document, elements=elements)
        document.grammar = grammar
        return document

    @staticmethod
    def create_requirement(
        first_sheet, document, row_num, columns: RequirementColumns
    ):
        row_values = first_sheet.row_values(row_num)
        statement = row_values[columns.statement_column]
        uid = None
        if columns.uid_column is not None:
            uid = row_values[columns.uid_column].strip()
        title = None
        if columns.title_column is not None:
            title = row_values[columns.title_column].strip()
        comments = None
        if columns.comment_column is not None:
            comment = row_values[columns.comment_column].strip()
            if comment in ("", "-"):
                comments = None
            else:
                comments = [comment]
        parent_uid = None
        if columns.parent_column is not None:
            parent_uid = row_values[columns.parent_column].strip()
        template_requirement = SDocObjectFactory.create_requirement(
            document,
            requirement_type="REQUIREMENT",
            title=title,
            uid=uid,
            level=None,
            statement=None,
            statement_multiline=statement,
            rationale=None,
            rationale_multiline=None,
            tags=None,
            comments=comments,
        )
        if parent_uid is not None:
            reference = Reference(template_requirement, "Parent", parent_uid)

            requirement_field = RequirementField(
                parent=template_requirement,
                field_name="REFS",
                field_value=None,
                field_value_multiline=None,
                field_value_references=[reference],
            )
            template_requirement.fields.append(requirement_field)
            template_requirement.ordered_fields_lookup["REFS"] = [
                requirement_field
            ]

        for i, name in columns.extra_header_pairs:
            value = row_values[i].strip()
            if value != "":
                template_requirement.fields.append(
                    RequirementField(
                        parent=None,
                        field_name=name,
                        field_value=None,
                        field_value_multiline=value,
                        field_value_references=None,
                    )
                )

        requirement = Requirement(
            parent=template_requirement.parent,
            requirement_type=template_requirement.requirement_type,
            fields=template_requirement.fields,
        )
        requirement.ng_level = 1

        return requirement
