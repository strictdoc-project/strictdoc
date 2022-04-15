import os
from typing import Optional, Any

import xlrd

from strictdoc.backend.sdoc.models.reference import Reference
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.requirement import (
    RequirementField,
    Requirement,
)
from strictdoc.backend.sdoc.models.type_system import GrammarElementFieldString


# pylint: disable=too-many-instance-attributes
class ExcelToSDocConverter:
    parent_column: int
    extra_header_pairs: Any
    criticality_column: int
    title_column: int
    comment_column: int
    uid_column: int
    statement_column: int

    def __init__(self, excel_file):
        self.excel_workbook = xlrd.open_workbook(
            filename=excel_file, on_demand=True
        )
        self.first_sheet = self.excel_workbook.sheet_by_index(0)
        self.header_row_num = self.lookup_header_row_num()
        self.excel_file_name = os.path.basename(excel_file)
        assert self.header_row_num is not None

    def lookup_header_row_num(self):
        for i in range(16):  # the first 16 rows should do ¯\_(ツ)_/¯
            if self.first_sheet.row_values(0)[0].strip() != "":
                return i
        return None

    def get_safe_header_row(self):
        header_row = self.first_sheet.row_values(self.header_row_num)
        header_row = list(self.safe_name(x) for x in header_row)
        return header_row

    def get_any_header_column(self, header_texts):
        if not isinstance(header_texts, list):
            header_texts = [header_texts]
        for text in header_texts:
            try:
                return self.get_safe_header_row().index(text)
            except ValueError:
                continue
        return -1

    @staticmethod
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

    def convert(self, title=None):
        if title is None:
            title = self.excel_file_name + " sheet " + self.first_sheet.name

        self.identify_all_columns()
        self.validate_all_required_columns()

        document = self.create_document(title)
        for i in range(self.header_row_num + 1, self.first_sheet.nrows):
            template_requirement = (
                self.create_template_requirement_from_well_known_columns(
                    document, i
                )
            )
            requirement = self.extend_requirement_with_extra_columns(
                template_requirement, i
            )
            document.section_contents.append(requirement)

        return document

    def identify_all_columns(self):
        all_header_columns = list(range(self.first_sheet.ncols))

        self.statement_column = self.get_any_header_column(
            ["REQUIREMENT", "STATEMENT"]
        )
        if self.statement_column != -1:
            all_header_columns.remove(self.statement_column)
        self.uid_column = self.get_any_header_column(
            ["REF", "REF #", "REF_#", "REFDES", "ID", "UID"]
        )
        if self.uid_column != -1:
            all_header_columns.remove(self.uid_column)
        self.comment_column = self.get_any_header_column(["REMARKS", "COMMENT"])
        if self.comment_column != -1:
            all_header_columns.remove(self.comment_column)
        self.title_column = self.get_any_header_column(["TITLE", "NAME"])
        if self.title_column != -1:
            all_header_columns.remove(self.title_column)
        self.parent_column = self.get_any_header_column(
            ["PARENT", "PARENT_REF", "PARENT_UID"]
        )
        if self.parent_column != -1:
            all_header_columns.remove(self.parent_column)

        header_row = self.get_safe_header_row()
        self.extra_header_pairs = list(
            map(lambda x: (x, header_row[x]), all_header_columns)
        )

    def validate_all_required_columns(self):
        assert self.statement_column != -1

    def create_document(self, title: Optional[str]) -> Document:
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
        for _, name in self.extra_header_pairs:
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

    def create_template_requirement_from_well_known_columns(
        self, document, row_num
    ):
        row_values = self.first_sheet.row_values(row_num)
        statement = row_values[self.statement_column]
        uid = None
        if self.uid_column != -1:
            uid = row_values[self.uid_column].strip()
        title = None
        if self.title_column != -1:
            title = row_values[self.title_column].strip()
        comments = None
        if self.comment_column != -1:
            comment = row_values[self.comment_column].strip()
            if comment in ("", "-"):
                comments = None
            else:
                comments = [comment]
        parent_uid = None
        if self.parent_column != -1:
            parent_uid = row_values[self.parent_column].strip()
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

        return template_requirement

    def extend_requirement_with_extra_columns(
        self, template_requirement, row_num
    ):
        row_values = self.first_sheet.row_values(row_num)
        fields = template_requirement.fields
        for i, name in self.extra_header_pairs:
            value = row_values[i].strip()
            if value != "":
                fields.append(
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
            fields=fields,
        )
        requirement.ng_level = 1
        return requirement

    @staticmethod
    def parse(input_path, title=None):
        converter = ExcelToSDocConverter(input_path)
        document = converter.convert(title)
        return document
