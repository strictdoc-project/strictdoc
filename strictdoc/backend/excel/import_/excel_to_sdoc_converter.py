"""
@relation(SDOC-SRS-152, scope=file)
"""

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

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


@dataclass
class ExcelSheetSchema:
    uid_column_idx: Optional[int]
    title_column_idx: Optional[int]
    statement_column_idx: Optional[int]
    comment_column_idx: Optional[int]
    parent_column_idx: Optional[int]
    extra_header_pairs: List[Tuple[int, str]]
    column_types: dict[int, bool]

    def is_column_multiline(self, column_idx: int) -> bool:
        return self.column_types.get(column_idx, False)


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

        header_column_indexes = list(range(sheet.ncols))

        # The first 16 rows should do ¯\_(ツ)_/¯.
        for i in range(16):
            if sheet.row_values(i)[0].strip() != "":
                header_row_idx = i
                break
        else:
            raise NotImplementedError

        header_row = sheet.row_values(header_row_idx)
        safe_header_row = [safe_name(x) for x in header_row]

        statement_column_idx = None
        uid_column_idx = None
        comment_column_idx = None
        title_column_idx = None
        parent_column_idx = None
        for header_column_idx_, header_column_title_ in enumerate(
            safe_header_row
        ):
            # Detect reserved field columns. The rest will be treated as extra
            # fields.
            if header_column_title_ in ("REQUIREMENT", "STATEMENT"):
                statement_column_idx = header_column_idx_
            elif header_column_title_ in (
                "REF",
                "REF #",
                "REF_#",
                "REFDES",
                "ID",
                "UID",
            ):
                uid_column_idx = header_column_idx_
            elif header_column_title_ in ("REMARKS", "COMMENT"):
                comment_column_idx = header_column_idx_
            elif header_column_title_ in ("TITLE", "NAME"):
                title_column_idx = header_column_idx_
            elif header_column_title_ in ("PARENT", "PARENT_REF", "PARENT_UID"):
                parent_column_idx = header_column_idx_
            else:
                continue
            header_column_indexes.remove(header_column_idx_)

        assert statement_column_idx is not None, (
            "Couldn't detect a column for requirement statements among the headers: "
            + ", ".join(safe_header_row)
        )

        extra_header_pairs: List[Tuple[int, str]] = list(
            map(lambda x: (x, safe_header_row[x]), header_column_indexes)
        )

        # For each column, check if it contains multiline values.
        # All rows must be checked, otherwise we might miss multiline values
        # that are only present in some rows. This is needed to determine
        # whether to treat the field as multiline in the SDoc document.
        column_types: dict[int, bool] = {}
        for i in range(header_row_idx + 1, sheet.nrows):
            row_values = sheet.row_values(i)
            for header_column_idx in header_column_indexes:
                value = str(row_values[header_column_idx]).strip()
                if (
                    isinstance(value, str)
                    and "\n" in value
                    or len(str(value)) > 60
                ):
                    column_types[header_column_idx] = True
                elif header_column_idx not in column_types:
                    column_types[header_column_idx] = False

        schema = ExcelSheetSchema(
            uid_column_idx=uid_column_idx,
            title_column_idx=title_column_idx,
            statement_column_idx=statement_column_idx,
            comment_column_idx=comment_column_idx,
            parent_column_idx=parent_column_idx,
            extra_header_pairs=extra_header_pairs,
            column_types=column_types,
        )
        document = ExcelToSDocConverter.create_document(
            title, extra_header_pairs
        )
        for i in range(header_row_idx + 1, sheet.nrows):
            row_values = sheet.row_values(i)
            requirement = ExcelToSDocConverter.create_requirement(
                row_values, document, schema
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
        field_titles = [f.title for f in fields]
        for _, name in extra_header_pairs:
            if name not in field_titles:
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
        schema: ExcelSheetSchema,
    ) -> SDocNode:
        assert schema.statement_column_idx is not None
        statement = row_values[schema.statement_column_idx].strip()
        uid = None
        if schema.uid_column_idx is not None:
            uid = row_values[schema.uid_column_idx].strip()
        title = None
        if schema.title_column_idx is not None:
            title = row_values[schema.title_column_idx].strip()
        comments = None
        if schema.comment_column_idx is not None:
            comment = row_values[schema.comment_column_idx].strip()
            if comment in ("", "-"):
                comments = None
            else:
                comments = [ensure_newline(comment)]
        parent_uid = None
        if schema.parent_column_idx is not None:
            parent_uid = row_values[schema.parent_column_idx].strip()
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
        for column_idx_, column_name_ in schema.extra_header_pairs:
            # For a field that looks like a decimal (e.g. LEVEL: 3.1), it gets
            # treated as a float and then this fails without string casting.
            # Cast to string and strip whitespace.
            value = str(row_values[column_idx_]).strip()
            if value == "":
                continue

            # Only treat field as a multiline if necessary.
            # This fixed a weird bug where the LEVEL field included
            # a carriage return, which then got oddly scooped into
            # the headings in the HTML view.
            if schema.is_column_multiline(column_idx_):
                multiline = True
                field_value = ensure_newline(value)
            else:
                multiline = False
                field_value = value
            template_requirement.ordered_fields_lookup[column_name_] = [
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=column_name_,
                    field_value=field_value,
                    multiline=multiline,
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
