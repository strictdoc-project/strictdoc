import html
from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional, Set

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.type_system import (
    FileEntry,
    FileEntryFormat,
    GrammarElementField,
    RequirementFieldType,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    RequirementConnections,
    TraceabilityIndex,
)
from strictdoc.core.tree_cycle_detector import (
    SingleShotTreeCycleDetector,
)
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.form_data import parse_form_data
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import sanitize_html_form_field
from strictdoc.server.error_object import ErrorObject


class RequirementFormFieldType(str, Enum):
    SINGLELINE = "SINGLELINE"
    MULTILINE = "MULTILINE"


@auto_described
class RequirementFormField:
    def __init__(
        self,
        field_mid: str,
        field_name: str,
        field_type: RequirementFormFieldType,
        field_unescaped_value: str,
        field_escaped_value: str,
    ):
        assert isinstance(field_unescaped_value, str)
        assert isinstance(field_escaped_value, str)
        self.field_mid: str = field_mid
        self.field_name: str = field_name
        self.field_type = field_type
        self.field_unescaped_value: str = field_unescaped_value
        self.field_escaped_value: str = field_escaped_value

    def is_singleline(self):
        return self.field_type == RequirementFormFieldType.SINGLELINE

    def is_multiline(self):
        return self.field_type == RequirementFormFieldType.MULTILINE

    def get_input_field_name(self):
        return f"requirement[fields][{self.field_mid}][value]"

    def get_input_field_type_name(self):
        return f"requirement[fields][{self.field_mid}][name]"

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
                field_mid=MID.create().get_string_value(),
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
                field_mid=MID.create().get_string_value(),
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
        PARENT = "Parent"
        CHILD = "Child"
        FILE = "File"

    def __init__(
        self,
        field_mid: str,
        field_type: FieldType,
        field_value: str,
        field_role: Optional[str],
    ):
        assert isinstance(field_mid, str), field_mid
        assert isinstance(field_value, str), field_value
        self.field_mid: str = field_mid
        self.field_type = field_type
        self.field_value: str = field_value
        self.field_role: str = (
            field_role if field_role is not None and len(field_role) > 0 else ""
        )
        self.validation_messages: List[str] = []

    def get_input_field_name(self):
        return "requirement_relation"

    def get_value_field_name(self):
        return f"requirement[relations][{self.field_mid}][value]"

    def get_type_field_name(self):
        return f"requirement[relations][{self.field_mid}][typerole]"


@auto_described
class RequirementFormObject(ErrorObject):
    def __init__(
        self,
        *,
        requirement_mid: Optional[str],
        document_mid: str,
        fields: List[RequirementFormField],
        reference_fields: List[RequirementReferenceFormField],
        exiting_requirement_uid: Optional[str],
        grammar: DocumentGrammar,
        # FIXME: Better name
        relation_types: List[str],
    ):
        super().__init__()
        self.requirement_mid: Optional[str] = requirement_mid
        self.document_mid: str = document_mid
        fields_dict: dict = defaultdict(list)
        for field in fields:
            fields_dict[field.field_name].append(field)
        self.fields: Dict[str, List[RequirementFormField]] = fields_dict
        self.reference_fields: List[
            RequirementReferenceFormField
        ] = reference_fields
        self.exiting_requirement_uid: Optional[str] = exiting_requirement_uid
        self.grammar: DocumentGrammar = grammar
        self.relation_types: List[str] = relation_types

    @staticmethod
    def create_from_request(
        *,
        requirement_mid: str,
        request_form_data: FormData,
        document: Document,
        exiting_requirement_uid: Optional[str],
    ) -> "RequirementFormObject":
        request_form_data_as_list = [
            (field_name, field_value)
            for field_name, field_value in request_form_data.multi_items()
        ]
        request_form_dict: Dict = assert_cast(
            parse_form_data(request_form_data_as_list), dict
        )
        requirement_fields = defaultdict(list)
        form_ref_fields: List[RequirementReferenceFormField] = []

        requirement_dict = request_form_dict["requirement"]
        requirement_fields_dict = requirement_dict["fields"]
        for _, field_dict in requirement_fields_dict.items():
            field_name = field_dict["name"]
            field_value = field_dict["value"]
            requirement_fields[field_name].append(field_value)

        # FIXME: defaulting to {}
        requirement_relations_dict = requirement_dict.get("relations", {})
        for relation_mid, relation_dict in requirement_relations_dict.items():
            # FIXME: Editing files is not supported. Fix this hack ASAP.
            relation_typerole = relation_dict.get("typerole", "File")
            relation_typerole_parts = relation_typerole.split(",")
            if len(relation_typerole_parts) == 2:
                relation_type = relation_typerole_parts[0]
                relation_role = relation_typerole_parts[1]
            elif len(relation_typerole_parts) == 1:
                relation_type = relation_typerole_parts[0]
                relation_role = None
            else:
                raise AssertionError("Must not reach here")
            field_type = (
                RequirementReferenceFormField.FieldType.PARENT
                if relation_type == "Parent"
                else RequirementReferenceFormField.FieldType.CHILD
                if relation_type == "Child"
                else RequirementReferenceFormField.FieldType.FILE
                if relation_type == "File"
                else ""
            )
            assert field_type in (
                RequirementReferenceFormField.FieldType.PARENT,
                RequirementReferenceFormField.FieldType.CHILD,
                RequirementReferenceFormField.FieldType.FILE,
            )
            relation_value = relation_dict["value"]

            form_ref_fields.append(
                RequirementReferenceFormField(
                    field_mid=relation_mid,
                    field_type=field_type,
                    field_value=relation_value,
                    field_role=relation_role,
                )
            )

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

        form_object = RequirementFormObject(
            requirement_mid=requirement_mid,
            document_mid=document.mid.get_string_value(),
            fields=form_fields,
            reference_fields=form_ref_fields,
            exiting_requirement_uid=exiting_requirement_uid,
            grammar=grammar,
            relation_types=element.get_relation_types(),
        )
        return form_object

    @staticmethod
    def create_new(
        *, document: Document, next_uid: str
    ) -> "RequirementFormObject":
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
            form_field: RequirementFormField = (
                RequirementFormField.create_from_grammar_field(
                    grammar_field=field,
                    multiline=field_idx > title_field_idx,
                    value_unescaped="",
                    value_escaped="",
                )
            )
            form_fields.append(form_field)
            if form_field.field_name == "UID":
                form_field.field_unescaped_value = next_uid
                form_field.field_escaped_value = next_uid

        return RequirementFormObject(
            requirement_mid=MID.create().get_string_value(),
            document_mid=document.mid.get_string_value(),
            fields=form_fields,
            reference_fields=[],
            exiting_requirement_uid=None,
            grammar=grammar,
            relation_types=element.get_relation_types(),
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

        grammar_element_relations = element.get_relation_types()

        form_fields: List[RequirementFormField] = []
        form_refs_fields: List[RequirementReferenceFormField] = []

        fields_names = list(element.fields_map.keys())
        title_field_idx = fields_names.index("TITLE")

        for field_idx, field_name in enumerate(fields_names):
            # First handle REFS fields in a special way.
            if field_name == "REFS":
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

        if "REFS" in requirement.ordered_fields_lookup:
            for requirement_field in requirement.ordered_fields_lookup["REFS"]:
                reference_value: Reference
                for reference_value in requirement_field.field_value_references:
                    if isinstance(reference_value, ParentReqReference):
                        parent_reference: ParentReqReference = reference_value
                        form_ref_field = RequirementReferenceFormField(
                            field_mid=parent_reference.mid.get_string_value(),
                            field_type=(
                                RequirementReferenceFormField.FieldType.PARENT
                            ),
                            field_value=parent_reference.ref_uid,
                            field_role=parent_reference.role,
                        )
                        form_refs_fields.append(form_ref_field)
                    elif isinstance(reference_value, ChildReqReference):
                        child_reference: ChildReqReference = reference_value
                        form_ref_field = RequirementReferenceFormField(
                            field_mid=child_reference.mid.get_string_value(),
                            field_type=(
                                RequirementReferenceFormField.FieldType.CHILD
                            ),
                            field_value=child_reference.ref_uid,
                            field_role=child_reference.role,
                        )
                        form_refs_fields.append(form_ref_field)
                    elif isinstance(reference_value, FileReference):
                        child_reference: FileReference = reference_value
                        form_ref_field = RequirementReferenceFormField(
                            field_mid=child_reference.mid.get_string_value(),
                            field_type=(
                                RequirementReferenceFormField.FieldType.FILE
                            ),
                            field_value=child_reference.get_posix_path(),
                            field_role=child_reference.role,
                        )
                        form_refs_fields.append(form_ref_field)
        return RequirementFormObject(
            requirement_mid=requirement.mid.get_string_value(),
            document_mid=document.mid.get_string_value(),
            fields=form_fields,
            reference_fields=form_refs_fields,
            exiting_requirement_uid=requirement.reserved_uid,
            grammar=grammar,
            relation_types=grammar_element_relations,
        )

    def any_errors(self):
        if super().any_errors():
            return True
        for reference_field in self.reference_fields:
            if len(reference_field.validation_messages) > 0:
                return True
        return False

    def get_requirement_relations(
        self, requirement: Requirement
    ) -> List[Reference]:
        references: List[Reference] = []
        reference_field: RequirementReferenceFormField
        for reference_field in self.reference_fields:
            ref_uid = reference_field.field_value
            ref_type = reference_field.field_type
            ref_role = reference_field.field_role
            if ref_type == RequirementReferenceFormField.FieldType.PARENT:
                references.append(
                    ParentReqReference(
                        parent=requirement, ref_uid=ref_uid, role=ref_role
                    )
                )
            elif ref_type == RequirementReferenceFormField.FieldType.CHILD:
                references.append(
                    ChildReqReference(
                        parent=requirement, ref_uid=ref_uid, role=ref_role
                    )
                )
            elif ref_type == RequirementReferenceFormField.FieldType.FILE:
                file_entry = FileEntry(
                    parent=requirement,
                    g_file_format=FileEntryFormat.SOURCECODE,
                    g_file_path=reference_field.field_value,
                )
                references.append(
                    FileReference(
                        parent=requirement,
                        g_file_entry=file_entry,
                    )
                )
            else:
                raise NotImplementedError(ref_type)
        return references

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

    def enumerate_relation_roles(
        self, relation_field: RequirementReferenceFormField
    ):
        requirement_element = self.grammar.elements_by_type["REQUIREMENT"]
        for relation_ in requirement_element.relations:
            is_current = (
                relation_field.field_type == relation_.relation_type
                and (
                    relation_field.field_role == relation_.relation_role
                    or (
                        relation_field.field_role == ""
                        and relation_.relation_role is None
                    )
                )
            )
            yield relation_.relation_type, relation_.relation_role, is_current

    def validate(
        self,
        *,
        traceability_index: TraceabilityIndex,
        context_document: Document,
        config: ProjectConfig,
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
                path_to_output_dir=config.export_output_dir,
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
                "Requirement with parent relations must have an UID. "
                "Either provide a parent UID, or "
                "delete the parent requirement relations.",
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
                    "parent requirement relations. For now, manually delete the "
                    "relations, rename the UID, recreate the relations.",
                )
            requirement_connections: RequirementConnections = (
                traceability_index.requirements_connections[
                    self.exiting_requirement_uid
                ]
            )
            if len(requirement_connections.children):
                self.add_error(
                    "UID",
                    "Not supported yet: "
                    "Renaming a requirement UID when the requirement has "
                    "child requirement relations. For now, manually delete the "
                    "relations, rename the UID, recreate the relations.",
                )
                return

        if requirement_uid is not None:
            relation_target_uids_so_far: Set[str] = set()
            for reference_field in self.reference_fields:
                if reference_field.field_type in ("Parent", "Child"):
                    link_uid = reference_field.field_value
                    if len(link_uid) == 0:
                        reference_field.validation_messages.append(
                            "Requirement relation UID must not be empty."
                        )
                        continue
                    elif (
                        link_uid
                        not in traceability_index.requirements_connections
                    ):
                        reference_field.validation_messages.append(
                            f'Parent requirement with an UID "{link_uid}" '
                            f"does not exist."
                        )
                        continue

                    # Validate that every UID can be only referenced once.
                    if link_uid in relation_target_uids_so_far:
                        reference_field.validation_messages.append(
                            f'A target requirement with a UID "{link_uid}" '
                            "is referenced more than once. Multiple relations "
                            "to the same target requirement are not allowed."
                        )
                        continue
                    relation_target_uids_so_far.add(link_uid)

                    # Check if the target document supports a given relation.
                    target_requirement: Requirement = (
                        traceability_index.get_node_by_uid(link_uid)
                    )
                    target_grammar_element: GrammarElement = (
                        target_requirement.document.grammar.elements_by_type[
                            "REQUIREMENT"
                        ]
                    )
                    field_role_or_none = (
                        reference_field.field_role
                        if reference_field.field_role is not None
                        and len(reference_field.field_role) > 0
                        else None
                    )
                    if not target_grammar_element.has_relation_type_role(
                        reference_field.field_type, field_role_or_none
                    ):
                        reference_field.validation_messages.append(
                            f"Relation target requirement's document "
                            "does not have this relation registered: "
                            f'type: "{reference_field.field_type}" '
                            f'role: "{reference_field.field_role}".'
                        )
                        continue

                    # Check if the relation forms a cycle.
                    ref_uid = reference_field.field_value

                    def parent_lambda(requirement_id_) -> List[str]:
                        return traceability_index.requirements_connections[
                            requirement_id_
                        ].get_parent_uids()

                    def child_lambda(requirement_id_) -> List[str]:
                        return traceability_index.requirements_connections[
                            requirement_id_
                        ].get_child_uids()

                    relations_lambda = (
                        parent_lambda
                        if reference_field.field_type == "Parent"
                        else child_lambda
                    )

                    cycle_detector = SingleShotTreeCycleDetector()
                    try:
                        cycle_detector.check_node(
                            requirement_uid,
                            ref_uid,
                            relations_lambda,
                        )
                    except DocumentTreeError as error_:
                        reference_field.validation_messages.append(
                            error_.to_validation_message()
                        )
