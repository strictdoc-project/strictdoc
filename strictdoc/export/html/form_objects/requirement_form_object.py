import html
from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional, Set

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.type_system import (
    FileEntry,
    FileEntryFormat,
    GrammarElementField,
    RequirementFieldType,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    SDocNodeConnections,
    TraceabilityIndex,
)
from strictdoc.core.tree_cycle_detector import SingleShotTreeCycleDetector
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
        self.field_unescaped_value: str = field_unescaped_value
        self.field_escaped_value: str = field_escaped_value
        self.field_type = field_type

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
    ) -> "RequirementFormField":
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
                field_mid=MID.create(),
                field_name=grammar_field.title,
                field_type=(
                    RequirementFormFieldType.MULTILINE
                    if multiline
                    else RequirementFormFieldType.SINGLELINE
                ),
                field_unescaped_value=value_unescaped,
                field_escaped_value=value_escaped,
            )
        raise NotImplementedError(grammar_field)

    @staticmethod
    def create_existing_from_grammar_field(
        grammar_field: GrammarElementField,
        multiline: bool,
        requirement_field: SDocNodeField,
    ) -> "RequirementFormField":
        if grammar_field.gef_type == RequirementFieldType.STRING:
            field_value = (
                requirement_field.field_value_multiline
                if requirement_field.field_value_multiline is not None
                else requirement_field.field_value
            )
            assert isinstance(field_value, str)
            escaped_field_value = html.escape(field_value)
            return RequirementFormField(
                field_mid=MID.create(),
                field_name=grammar_field.title,
                field_type=(
                    RequirementFormFieldType.MULTILINE
                    if multiline
                    else RequirementFormFieldType.SINGLELINE
                ),
                field_unescaped_value=field_value,
                field_escaped_value=escaped_field_value,
            )
        raise NotImplementedError(grammar_field)

    @staticmethod
    def create_mid_field(mid: MID) -> "RequirementFormField":
        return RequirementFormField(
            field_mid=MID.create(),
            field_name="MID",
            field_type=RequirementFormFieldType.SINGLELINE,
            field_unescaped_value=mid,
            field_escaped_value=html.escape(mid),
        )


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
    """
    context_document_mid: The MID of the document where the requirement is edited.
                          Normally, this is the requirement's own document but can
                          also be the parent document if requirement's own document
                          is included to it.
    """

    def __init__(
        self,
        *,
        is_new: bool,
        element_type: str,
        requirement_mid: Optional[str],
        document_mid: str,
        context_document_mid: str,
        mid_field: Optional[RequirementFormField],
        fields: List[RequirementFormField],
        reference_fields: List[RequirementReferenceFormField],
        exiting_requirement_uid: Optional[str],
        grammar: DocumentGrammar,
        # FIXME: Better name
        relation_types: List[str],
    ):
        super().__init__()
        assert isinstance(element_type, str), element_type
        self.is_new: bool = is_new
        self.element_type: str = element_type
        self.requirement_mid: Optional[str] = requirement_mid
        self.document_mid: str = document_mid
        self.context_document_mid: str = context_document_mid
        self.mid_field: Optional[RequirementFormField] = mid_field
        fields_dict: dict = defaultdict(list)
        for field in fields:
            fields_dict[field.field_name].append(field)
        self.fields: Dict[str, List[RequirementFormField]] = fields_dict
        self.reference_fields: List[RequirementReferenceFormField] = (
            reference_fields
        )
        self.exiting_requirement_uid: Optional[str] = exiting_requirement_uid
        self.grammar: DocumentGrammar = grammar
        self.relation_types: List[str] = relation_types

    @staticmethod
    def create_from_request(
        *,
        is_new: bool,
        requirement_mid: str,
        request_form_data: FormData,
        document: SDocDocument,
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

        context_document_mid = request_form_dict["context_document_mid"]
        requirement_dict = request_form_dict["requirement"]

        element_type = request_form_dict["element_type"]
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
                else (
                    RequirementReferenceFormField.FieldType.CHILD
                    if relation_type == "Child"
                    else (
                        RequirementReferenceFormField.FieldType.FILE
                        if relation_type == "File"
                        else ""
                    )
                )
            )
            assert field_type in (
                RequirementReferenceFormField.FieldType.PARENT,
                RequirementReferenceFormField.FieldType.CHILD,
                RequirementReferenceFormField.FieldType.FILE,
            )
            relation_value = relation_dict["value"].strip()

            form_ref_fields.append(
                RequirementReferenceFormField(
                    field_mid=relation_mid,
                    field_type=field_type,
                    field_value=relation_value,
                    field_role=relation_role,
                )
            )

        # MID field is handled separately from other fields because it not part
        # of any grammar, default or user-provided.
        mid_field: Optional[RequirementFormField] = None
        if "MID" in requirement_fields:
            requirement_field_values = requirement_fields.get("MID", [])
            for requirement_field_value in requirement_field_values:
                sanitized_field_value: str = sanitize_html_form_field(
                    requirement_field_value, multiline=False
                )
                mid_field: RequirementFormField = (
                    RequirementFormField.create_mid_field(
                        MID(sanitized_field_value)
                    )
                )

                # This is where the original requirement MID auto-generated
                # for a new requirement by StrictDoc can change because
                # a user has provided a new one in the input form.
                requirement_mid = sanitized_field_value

        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type[element_type]
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
                    requirement_field_value, multiline=multiline
                )
                form_field = RequirementFormField.create_from_grammar_field(
                    grammar_field=field,
                    multiline=multiline,
                    value_unescaped=sanitized_field_value,
                    value_escaped=html.escape(sanitized_field_value),
                )
                form_fields.append(form_field)

        form_object = RequirementFormObject(
            is_new=is_new,
            element_type=element_type,
            requirement_mid=requirement_mid,
            document_mid=document.reserved_mid,
            context_document_mid=context_document_mid,
            mid_field=mid_field,
            fields=form_fields,
            reference_fields=form_ref_fields,
            exiting_requirement_uid=exiting_requirement_uid,
            grammar=grammar,
            relation_types=element.get_relation_types(),
        )
        return form_object

    @staticmethod
    def create_new(
        *,
        document: SDocDocument,
        context_document_mid: str,
        next_uid: str,
        element_type: str,
    ) -> "RequirementFormObject":
        assert document.grammar is not None

        new_requirement_mid: MID = MID.create()

        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type[element_type]

        mid_field: Optional[RequirementFormField] = None
        if document.config.enable_mid:
            mid_field: RequirementFormField = (
                RequirementFormField.create_mid_field(new_requirement_mid)
            )
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
            is_new=True,
            element_type=element_type,
            requirement_mid=new_requirement_mid,
            document_mid=document.reserved_mid,
            context_document_mid=context_document_mid,
            mid_field=mid_field,
            fields=form_fields,
            reference_fields=[],
            exiting_requirement_uid=None,
            grammar=grammar,
            relation_types=element.get_relation_types(),
        )

    @staticmethod
    def create_from_requirement(
        *,
        requirement: SDocNode,
        context_document_mid: str,
    ) -> "RequirementFormObject":
        assert isinstance(requirement, SDocNode)
        document: SDocDocument = requirement.document
        assert document.grammar is not None
        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type[
            requirement.requirement_type
        ]

        mid_field: Optional[RequirementFormField] = None
        if document.config.enable_mid:
            mid_field: RequirementFormField = (
                RequirementFormField.create_mid_field(requirement.reserved_mid)
            )

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
                            field_mid=parent_reference.mid,
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
                            field_mid=child_reference.mid,
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
                            field_mid=child_reference.mid,
                            field_type=(
                                RequirementReferenceFormField.FieldType.FILE
                            ),
                            field_value=child_reference.get_posix_path(),
                            field_role=child_reference.role,
                        )
                        form_refs_fields.append(form_ref_field)
        return RequirementFormObject(
            is_new=False,
            element_type=requirement.requirement_type,
            requirement_mid=requirement.reserved_mid,
            document_mid=document.reserved_mid,
            context_document_mid=context_document_mid,
            mid_field=mid_field,
            fields=form_fields,
            reference_fields=form_refs_fields,
            exiting_requirement_uid=requirement.reserved_uid,
            grammar=grammar,
            relation_types=grammar_element_relations,
        )

    @staticmethod
    def clone_from_requirement(
        *, requirement: SDocNode, context_document_mid: str, clone_uid: str
    ) -> "RequirementFormObject":
        form_object: RequirementFormObject = (
            RequirementFormObject.create_from_requirement(
                requirement=requirement,
                context_document_mid=context_document_mid,
            )
        )
        for field_name, fields_ in form_object.fields.items():
            if field_name == "UID":
                field: RequirementFormField = fields_[0]
                field.field_unescaped_value = clone_uid
                field.field_escaped_value = clone_uid
        form_object.requirement_mid = MID.create()

        return form_object

    def any_errors(self):
        if super().any_errors():
            return True
        for reference_field in self.reference_fields:
            if len(reference_field.validation_messages) > 0:
                return True
        return False

    def get_requirement_relations(
        self, requirement: SDocNode
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
                    g_line_range="",
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
        requirement_element = self.grammar.elements_by_type[self.element_type]
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
        context_document: SDocDocument,
        config: ProjectConfig,
    ):
        assert isinstance(traceability_index, TraceabilityIndex)
        assert isinstance(context_document, SDocDocument)

        if self.is_new and self.mid_field is not None:
            existing_node_with_this_mid = (
                traceability_index.get_node_by_mid_weak(
                    MID(self.mid_field.field_unescaped_value)
                )
            )
            if existing_node_with_this_mid is not None:
                self.add_error(
                    "MID",
                    (
                        f"A node with this MID already exists, "
                        "please select another MID: "
                        f"{self.mid_field.field_unescaped_value}."
                    ),
                )

        if self.is_new and "UID" in self.fields:
            requirement_uid = self.fields["UID"][0].field_unescaped_value
            existing_node_with_this_uid = (
                traceability_index.get_node_by_uid_weak(requirement_uid)
            )
            if existing_node_with_this_uid is not None:
                self.add_error(
                    "UID",
                    (
                        "The chosen UID must be unique. "
                        "Another node with this UID already exists: "
                        f"'{requirement_uid}'."
                    ),
                )

        requirement_statement = self.fields["STATEMENT"][
            0
        ].field_unescaped_value
        if requirement_statement is None or len(requirement_statement) == 0:
            self.add_error(
                "STATEMENT",
                "Node statement must not be empty.",
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
            requirement_connections: SDocNodeConnections = (
                traceability_index.get_node_connections(
                    self.exiting_requirement_uid
                )
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
                    elif not traceability_index.has_node_connections(link_uid):
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
                    target_requirement: SDocNode = (
                        traceability_index.get_node_by_uid(link_uid)
                    )
                    target_grammar_element: GrammarElement = (
                        target_requirement.document.grammar.elements_by_type[
                            self.element_type
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
                        return traceability_index.get_node_connections(
                            requirement_id_
                        ).get_parent_uids()

                    def child_lambda(requirement_id_) -> List[str]:
                        return traceability_index.get_node_connections(
                            requirement_id_
                        ).get_child_uids()

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
