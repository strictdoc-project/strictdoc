import html
import re
import uuid
from collections import OrderedDict
from enum import Enum
from typing import Optional, List, Dict

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementField,
    RequirementFieldType,
)
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.string import sanitize_html_form_field
from strictdoc.server.error_object import ErrorObject


class RequirementFormFieldType(str, Enum):
    SINGLELINE = "SINGLELINE"
    MULTILINE = "MULTILINE"


@auto_described
class RequirementFormField:
    def __init__(
        self,
        field_name: str,
        field_type: RequirementFormFieldType,
        field_value: Optional[str],
    ):
        self.field_name = field_name
        self.field_type = field_type
        self.field_value = (
            field_value
            if field_value is not None and len(field_value) > 0
            else ""
        )

    def is_singleline(self):
        return self.field_type == RequirementFormFieldType.SINGLELINE

    def is_multiline(self):
        return self.field_type == RequirementFormFieldType.MULTILINE

    @staticmethod
    def create_from_grammar_field(
        *,
        grammar_field: GrammarElementField,
        multiline: bool,
        value: Optional[str],
    ):
        if value is not None:
            value = html.escape(value)
        if grammar_field.gef_type == RequirementFieldType.STRING:
            return RequirementFormField(
                field_name=grammar_field.title,
                field_type=RequirementFormFieldType.MULTILINE
                if multiline
                else RequirementFormFieldType.SINGLELINE,
                field_value=value,
            )
        raise NotImplementedError(grammar_field)

    @staticmethod
    def create_existing_from_grammar_field(
        grammar_field: GrammarElementField,
        multiline: bool,
        requirement_field: RequirementField,
    ):
        if grammar_field.gef_type == RequirementFieldType.STRING:
            field_value = (
                requirement_field.field_value_multiline
                if requirement_field.field_value_multiline is not None
                else requirement_field.field_value
            )
            if field_value is not None:
                field_value = html.escape(field_value)
            return RequirementFormField(
                field_name=grammar_field.title,
                field_type=RequirementFormFieldType.MULTILINE
                if multiline
                else RequirementFormFieldType.SINGLELINE,
                field_value=field_value,
            )
        raise NotImplementedError(grammar_field)


@auto_described
class RequirementFormObject(ErrorObject):
    def __init__(
        self,
        *,
        requirement_mid: Optional[str],
        fields: List[RequirementFormField],
    ):
        super().__init__()
        self.requirement_mid: Optional[str] = requirement_mid
        fields_dict: dict = OrderedDict()
        for field in fields:
            fields_dict[field.field_name] = field
        self.fields: Dict[str, RequirementFormField] = fields_dict

    @staticmethod
    def create_from_request(
        *, requirement_mid: str, request_dict: dict, document: Document
    ) -> "RequirementFormObject":
        requirement_fields = {}
        for field_name, field_value in request_dict.items():
            result = re.search(r"^requirement\[(.*)]$", field_name)
            if result is not None:
                requirement_fields[result.group(1)] = field_value

        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type["REQUIREMENT"]
        form_fields: List[RequirementFormField] = []

        fields_names = list(element.fields_map.keys())
        title_field_idx = fields_names.index("TITLE")

        for field_idx, field_name in enumerate(fields_names):
            if field_name == "REFS":
                continue
            multiline = field_idx > title_field_idx
            field = element.fields_map[field_name]

            field_value: Optional[str] = None
            if field_name in requirement_fields:
                field_value = requirement_fields.get(field_name, None)
                field_value = sanitize_html_form_field(
                    field_value, multiline=True
                )
            form_field = RequirementFormField.create_from_grammar_field(
                grammar_field=field, multiline=multiline, value=field_value
            )
            form_fields.append(form_field)

        return RequirementFormObject(
            requirement_mid=requirement_mid,
            fields=form_fields,
        )

    @staticmethod
    def create_new(*, document: Document) -> "RequirementFormObject":
        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type["REQUIREMENT"]
        form_fields: List[RequirementFormField] = []

        fields_names = list(element.fields_map.keys())
        title_field_idx = fields_names.index("TITLE")

        for field_idx, field_name in enumerate(fields_names):
            if field_name == "REFS":
                continue

            field = element.fields_map[field_name]
            form_field = RequirementFormField.create_from_grammar_field(
                grammar_field=field,
                multiline=field_idx > title_field_idx,
                value=None,
            )
            form_fields.append(form_field)

        return RequirementFormObject(
            requirement_mid=uuid.uuid4().hex,
            fields=form_fields,
        )

    @staticmethod
    def create_from_requirement(
        *, requirement: Requirement
    ) -> "RequirementFormObject":
        assert isinstance(requirement, Requirement)
        document: Document = requirement.document
        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type["REQUIREMENT"]
        form_fields: List[RequirementFormField] = []

        fields_names = list(element.fields_map.keys())
        title_field_idx = fields_names.index("TITLE")

        for field_idx, field_name in enumerate(fields_names):
            if field_name == "REFS":
                continue

            field = element.fields_map[field_name]

            if field_name in requirement.ordered_fields_lookup:
                requirement_field: RequirementField = (
                    requirement.ordered_fields_lookup[field_name][0]
                )
                form_field = (
                    RequirementFormField.create_existing_from_grammar_field(
                        field,
                        multiline=field_idx > title_field_idx,
                        requirement_field=requirement_field,
                    )
                )
            else:
                form_field = RequirementFormField.create_from_grammar_field(
                    grammar_field=field,
                    multiline=field_idx > title_field_idx,
                    value=None,
                )
            form_fields.append(form_field)
        return RequirementFormObject(
            requirement_mid=requirement.node_id,
            fields=form_fields,
        )

    def enumerate_fields(self):
        for field_name, field in self.fields.items():
            yield field

    def validate(self):
        requirement_statement = self.fields["STATEMENT"].field_value
        if requirement_statement is None or len(requirement_statement) == 0:
            self.add_error(
                "STATEMENT",
                "Requirement statement must not be empty.",
            )
        else:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter.write_with_validation(
                requirement_statement
            )
            if parsed_html is None:
                self.add_error("STATEMENT", rst_error)
