import html
import re
import uuid
from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.reference import (
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementField,
    RequirementFieldType,
)
from strictdoc.core.traceability_index import (
    RequirementConnections,
    TraceabilityIndex,
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
        field_unescaped_value: str,
        field_escaped_value: str,
    ):
        assert isinstance(field_unescaped_value, str)
        assert isinstance(field_escaped_value, str)
        self.field_name: str = field_name
        self.field_type = field_type
        self.field_unescaped_value: str = field_unescaped_value
        self.field_escaped_value: str = field_escaped_value

    def is_singleline(self):
        return self.field_type == RequirementFormFieldType.SINGLELINE

    def is_multiline(self):
        return self.field_type == RequirementFormFieldType.MULTILINE

    @staticmethod
    def create_from_grammar_field(
        *,
        grammar_field: GrammarElementField,
        multiline: bool,
        value_unescaped: str,
        value_escaped: str,
    ):
        assert isinstance(value_unescaped, str), (
            grammar_field,
            multiline,
            value_unescaped,
        )
        assert isinstance(value_escaped, str), (
            grammar_field,
            multiline,
            value_escaped,
        )
        if grammar_field.gef_type == RequirementFieldType.STRING:
            return RequirementFormField(
                field_name=grammar_field.title,
                field_type=RequirementFormFieldType.MULTILINE
                if multiline
                else RequirementFormFieldType.SINGLELINE,
                field_unescaped_value=value_unescaped,
                field_escaped_value=value_escaped,
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
            assert isinstance(field_value, str)
            escaped_field_value = html.escape(field_value)
            return RequirementFormField(
                field_name=grammar_field.title,
                field_type=RequirementFormFieldType.MULTILINE
                if multiline
                else RequirementFormFieldType.SINGLELINE,
                field_unescaped_value=field_value,
                field_escaped_value=escaped_field_value,
            )
        raise NotImplementedError(grammar_field)


@auto_described
class RequirementReferenceFormField:
    class FieldType(str, Enum):
        PARENT = "PARENT"

    def __init__(
        self,
        field_type: FieldType,
        field_value: str,
    ):
        assert isinstance(field_value, str), field_value
        self.field_type = field_type
        self.field_value: str = field_value
        self.validation_messages: List[str] = []


@auto_described
class RequirementFormObject(ErrorObject):
    def __init__(
        self,
        *,
        requirement_mid: Optional[str],
        fields: List[RequirementFormField],
        reference_fields: List[RequirementReferenceFormField],
        exiting_requirement_uid: Optional[str],
    ):
        super().__init__()
        self.requirement_mid: Optional[str] = requirement_mid
        fields_dict: dict = defaultdict(list)
        for field in fields:
            fields_dict[field.field_name].append(field)
        self.fields: Dict[str, List[RequirementFormField]] = fields_dict
        self.reference_fields: List[
            RequirementReferenceFormField
        ] = reference_fields
        self.exiting_requirement_uid: Optional[str] = exiting_requirement_uid

    @staticmethod
    def create_from_request(
        *,
        requirement_mid: str,
        request_form_data: FormData,
        document: Document,
        exiting_requirement_uid: Optional[str],
    ) -> "RequirementFormObject":
        requirement_fields = defaultdict(list)
        parent_refs: List[str] = []
        for field_name, field_value in request_form_data.multi_items():
            if field_name == "requirement[REFS_PARENT][]":
                parent_refs.append(field_value)
                continue

            result = re.search(r"^requirement\[(.*)]$", field_name)
            if result is not None:
                requirement_fields[result.group(1)].append(field_value)

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

            if field_name not in requirement_fields:
                continue

            requirement_field_values = requirement_fields.get(field_name, [])
            for requirement_field_value in requirement_field_values:
                sanitized_field_value: str = sanitize_html_form_field(
                    requirement_field_value, multiline=True
                )
                form_field = RequirementFormField.create_from_grammar_field(
                    grammar_field=field,
                    multiline=multiline,
                    value_unescaped=sanitized_field_value,
                    value_escaped=html.escape(sanitized_field_value),
                )
                form_fields.append(form_field)

        form_ref_fields: List[RequirementReferenceFormField] = []
        for parent_ref in parent_refs:
            form_ref_fields.append(
                RequirementReferenceFormField(
                    field_type=(RequirementReferenceFormField.FieldType.PARENT),
                    field_value=parent_ref,
                )
            )
        form_object = RequirementFormObject(
            requirement_mid=requirement_mid,
            fields=form_fields,
            reference_fields=form_ref_fields,
            exiting_requirement_uid=exiting_requirement_uid,
        )
        return form_object

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
                value_unescaped="",
                value_escaped="",
            )
            form_fields.append(form_field)

        return RequirementFormObject(
            requirement_mid=uuid.uuid4().hex,
            fields=form_fields,
            reference_fields=[],
            exiting_requirement_uid=None,
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
        form_refs_fields: List[RequirementReferenceFormField] = []

        fields_names = list(element.fields_map.keys())
        title_field_idx = fields_names.index("TITLE")

        for field_idx, field_name in enumerate(fields_names):
            # First handle REFS fields in a special way.
            if field_name == "REFS":
                if field_name not in requirement.ordered_fields_lookup:
                    continue
                for requirement_field in requirement.ordered_fields_lookup[
                    "REFS"
                ]:
                    reference_value: Reference
                    for (
                        reference_value
                    ) in requirement_field.field_value_references:
                        if not isinstance(reference_value, ParentReqReference):
                            continue
                        parent_reference: ParentReqReference = reference_value
                        form_ref_field = RequirementReferenceFormField(
                            field_type=(
                                RequirementReferenceFormField.FieldType.PARENT
                            ),
                            field_value=parent_reference.ref_uid,
                        )
                        form_refs_fields.append(form_ref_field)
                continue

            # Handle all other fields in a general way.
            field = element.fields_map[field_name]

            if field_name in requirement.ordered_fields_lookup:
                for requirement_field in requirement.ordered_fields_lookup[
                    field_name
                ]:
                    form_field = (
                        RequirementFormField.create_existing_from_grammar_field(
                            field,
                            multiline=field_idx > title_field_idx,
                            requirement_field=requirement_field,
                        )
                    )
                    form_fields.append(form_field)
            else:
                form_field = RequirementFormField.create_from_grammar_field(
                    grammar_field=field,
                    multiline=field_idx > title_field_idx,
                    value_unescaped="",
                    value_escaped="",
                )
                form_fields.append(form_field)
        return RequirementFormObject(
            requirement_mid=requirement.node_id,
            fields=form_fields,
            reference_fields=form_refs_fields,
            exiting_requirement_uid=requirement.reserved_uid,
        )

    def any_errors(self):
        if super().any_errors():
            return True
        for reference_field in self.reference_fields:
            if len(reference_field.validation_messages) > 0:
                return True
        return False

    def enumerate_fields(self, multiline: bool):
        for _, field in self.fields.items():
            requirement_field: RequirementFormField = field[0]
            if multiline:
                if not requirement_field.is_multiline():
                    continue
            else:
                if requirement_field.is_multiline():
                    continue
            yield field

    def enumerate_reference_fields(self):
        yield from self.reference_fields

    def validate(
        self,
        *,
        traceability_index: TraceabilityIndex,
        context_document: Document,
    ):
        assert isinstance(traceability_index, TraceabilityIndex)
        assert isinstance(context_document, Document)
        requirement_statement = self.fields["STATEMENT"][
            0
        ].field_unescaped_value
        if requirement_statement is None or len(requirement_statement) == 0:
            self.add_error(
                "STATEMENT",
                "Requirement statement must not be empty.",
            )
        else:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter(
                context_document=context_document,
            ).write_with_validation(requirement_statement)
            if parsed_html is None:
                self.add_error("STATEMENT", rst_error)

        requirement_uid: Optional[str] = (
            self.fields["UID"][0].field_unescaped_value
            if "UID" in self.fields
            else None
        )
        if len(self.reference_fields) > 0 and (
            requirement_uid is None or len(requirement_uid) == 0
        ):
            self.add_error(
                "UID",
                "Requirement with parent links must have an UID. "
                "Either provide a parent UID, or "
                "delete the parent requirement links.",
            )

        if (
            self.exiting_requirement_uid is not None
            and self.exiting_requirement_uid != requirement_uid
        ):
            if len(self.reference_fields) > 0:
                self.add_error(
                    "UID",
                    "Not supported yet: "
                    "Renaming a requirement UID when the requirement has "
                    "parent requirement links. For now, manually delete the "
                    "links, rename the UID, recreate the links.",
                )
            requirement_connections: RequirementConnections = (
                traceability_index.requirements_parents[
                    self.exiting_requirement_uid
                ]
            )
            if len(requirement_connections.children):
                self.add_error(
                    "UID",
                    "Not supported yet: "
                    "Renaming a requirement UID when the requirement has "
                    "child requirement links. For now, manually delete the "
                    "links, rename the UID, recreate the links.",
                )
        for reference_field in self.reference_fields:
            link_uid = reference_field.field_value
            if len(link_uid) == 0:
                reference_field.validation_messages.append(
                    "Requirement parent link UID must not be empty."
                )
            elif link_uid not in traceability_index.requirements_parents:
                reference_field.validation_messages.append(
                    f'Parent requirement with an UID "{link_uid}" '
                    f"does not exist."
                )
