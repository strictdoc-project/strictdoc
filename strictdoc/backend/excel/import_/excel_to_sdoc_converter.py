"""
@relation(SDOC-SRS-152, scope=file)
"""

# mypy: disable-error-code="no-untyped-call"
import os
from typing import List, NamedTuple, Optional, Tuple, Union

from strictdoc.backend.excel.import_.excel_sheet_proxy import ExcelSheetProxy
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementFieldString,
)
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import ParentReqReference
from strictdoc.helpers.string import ensure_newline


class RequirementColumns(NamedTuple):
    uid_column: Optional[int]
    title_column: Optional[int]
    statement_column: Optional[int]
    comment_column: Optional[int]
    parent_column: Optional[int]
    extra_header_pairs: List[Tuple[int, str]]


def safe_name(dangerous_name: str) -> str:
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


class ExcelToSDocConverter:
    @staticmethod
    def convert(
        excel_file: str, title: Union[str, None] = None
    ) -> SDocDocument:
        """
        Convert a provided Excel file to an SDoc document.

        Optional argument title is present for external scripts to assign a title.
        """
        sheet = ExcelSheetProxy(excel_file)

        excel_file_name = os.path.basename(excel_file)
        if title is None:
            title = excel_file_name + " sheet " + sheet.name

        all_header_columns = list(range(sheet.ncols))

        # The first 16 rows should do ¯\_(ツ)_/¯.
        for i in range(16):
            if sheet.row_values(i)[0].strip() != "":
                header_row_idx = i
                break
        else:
            raise NotImplementedError

        header_row = sheet.row_values(header_row_idx)
        safe_header_row = [safe_name(x) for x in header_row]

        statement_column = None
        uid_column = None
        comment_column = None
        title_column = None
        parent_column = None
        for header_column_idx, header_column in enumerate(safe_header_row):
            if header_column in ("REQUIREMENT", "STATEMENT"):
                statement_column = header_column_idx
            elif header_column in (
                "REF",
                "REF #",
                "REF_#",
                "REFDES",
                "ID",
                "UID",
            ):
                uid_column = header_column_idx
            elif header_column in ("REMARKS", "COMMENT"):
                comment_column = header_column_idx
            elif header_column in ("TITLE", "NAME"):
                title_column = header_column_idx
            elif header_column in ("PARENT", "PARENT_REF", "PARENT_UID"):
                parent_column = header_column_idx
            else:
                continue
            all_header_columns.remove(header_column_idx)
        assert statement_column is not None

        extra_header_pairs: List[Tuple[int, str]] = list(
            map(lambda x: (x, safe_header_row[x]), all_header_columns)
        )
        columns = RequirementColumns(
            uid_column=uid_column,
            title_column=title_column,
            statement_column=statement_column,
            comment_column=comment_column,
            parent_column=parent_column,
            extra_header_pairs=extra_header_pairs,
        )

        document = ExcelToSDocConverter.create_document(
            title, extra_header_pairs
        )
        for i in range(header_row_idx + 1, sheet.nrows):
            row_values = sheet.row_values(i)
            requirement = ExcelToSDocConverter.create_requirement(
                row_values, document, columns
            )
            document.section_contents.append(requirement)

        return document

    @staticmethod
    def create_document(
        title: Optional[str], extra_header_pairs: List[Tuple[int, str]]
    ) -> SDocDocument:
        document_config = DocumentConfig.default_config(None)
        document_title = title if title else "<No title>"
        document = SDocDocument(
            mid=None,
            title=document_title,
            config=document_config,
            view=None,
            grammar=None,
            section_contents=[],
        )

        # FIXME: This is becoming very limiting. It must work against a complete grammar.
        fields = list(
            DocumentGrammar.create_default(document)
            .elements_by_type["REQUIREMENT"]
            .fields
        )

        for _, name in extra_header_pairs:
            fields.extend(
                [
                    GrammarElementFieldString(
                        parent=None,
                        title=name,
                        human_title=None,
                        required="False",
                    ),
                ]
            )

        requirements_element = GrammarElement(
            parent=None,
            tag="REQUIREMENT",
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[],
        )
        elements = [requirements_element]
        grammar = DocumentGrammar(parent=document, elements=elements)
        document.grammar = grammar
        return document

    @staticmethod
    def create_requirement(
        row_values: List[str],
        document: SDocDocument,
        columns: RequirementColumns,
    ) -> SDocNode:
        assert columns.statement_column is not None
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
                comments = [ensure_newline(comment)]
        parent_uid = None
        if columns.parent_column is not None:
            parent_uid = row_values[columns.parent_column].strip()
            if len(parent_uid) == 0:
                parent_uid = None

        template_requirement = SDocObjectFactory.create_requirement(
            document,
            node_type="REQUIREMENT",
            title=title,
            uid=uid,
            level=None,
            statement=None,
            statement_multiline=ensure_newline(statement),
            rationale=None,
            rationale_multiline=None,
            tags=None,
            comments=comments,
        )
        for i, name in columns.extra_header_pairs:
            value = row_values[i].strip()
            if value != "":
                template_requirement.ordered_fields_lookup[name] = [
                    SDocNodeField.create_from_string(
                        parent=None,
                        field_name=name,
                        field_value=ensure_newline(value),
                        multiline=True,
                    )
                ]
        if parent_uid is not None:
            reference = ParentReqReference(
                template_requirement, parent_uid, role=None
            )
            template_requirement.relations = [reference]
        requirement = SDocNode(
            parent=template_requirement.parent,
            node_type=template_requirement.node_type,
            fields=list(template_requirement.enumerate_fields()),
            relations=template_requirement.relations,
        )

        return requirement
