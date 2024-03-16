from copy import copy
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import (
    Reference,
)
from strictdoc.backend.sdoc.models.type_system import RequirementFieldName
from strictdoc.core.traceability_index import (
    GraphLinkType,
    SDocNodeConnections,
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
)


class UpdateRequirementActionObject:
    def __init__(self):
        self.existing_references_uids: Set[Tuple[str, str, Optional[str]]] = (
            set()
        )
        self.reference_ids_to_remove: Set[Tuple[str, str, Optional[str]]] = (
            set()
        )
        self.removed_uid_parent_documents_to_update: Set[SDocDocument] = set()
        # All requirements that have to be updated. This set includes
        # the requirement itself, all links it was linking to
        # (for deleted links) and all links it is linking to now
        # (including new links).
        self.this_document_requirements_to_update: Set[SDocNode] = set()


@dataclass
class UpdateRequirementResult:
    this_document_requirements_to_update: Set[SDocNode]


class UpdateRequirementTransform:
    def __init__(
        self,
        *,
        form_object: RequirementFormObject,
        requirement: SDocNode,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: RequirementFormObject = form_object
        self.requirement: SDocNode = requirement
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        form_object: RequirementFormObject = self.form_object
        requirement: SDocNode = self.requirement
        document: SDocDocument = requirement.document
        traceability_index: TraceabilityIndex = self.traceability_index

        existing_uid: Optional[str] = requirement.reserved_uid

        # Clearing all existing fields because they will be recreated from
        # scratch from the form data.
        requirement.ordered_fields_lookup.clear()
        requirement.ng_reserved_fields_cache.clear()

        for form_field_name, form_fields in form_object.fields.items():
            for form_field_index, form_field in enumerate(form_fields):
                requirement.set_field_value(
                    field_name=form_field_name,
                    form_field_index=form_field_index,
                    value=form_field.field_unescaped_value,
                )

        action_object = UpdateRequirementActionObject()
        action_object.existing_references_uids.update(
            requirement.get_requirement_reference_uids()
        )
        action_object.reference_ids_to_remove = copy(
            action_object.existing_references_uids
        )
        action_object.this_document_requirements_to_update = {requirement}

        references: List[Reference] = form_object.get_requirement_relations(
            requirement
        )

        if len(references) > 0:
            requirement.ordered_fields_lookup[RequirementFieldName.REFS] = [
                SDocNodeField(
                    parent=requirement,
                    field_name=RequirementFieldName.REFS,
                    field_value=None,
                    field_value_multiline=None,
                    field_value_references=references,
                )
            ]
            requirement.references = references
        else:
            if RequirementFieldName.REFS in requirement.ordered_fields_lookup:
                del requirement.ordered_fields_lookup[RequirementFieldName.REFS]
            requirement.references = []

        for document_ in traceability_index.document_tree.document_list:
            document_.ng_needs_generation = False

        # Updating Traceability Index: Links
        for reference_field in form_object.reference_fields:
            ref_uid = reference_field.field_value
            ref_role: Optional[str] = (
                reference_field.field_role
                if reference_field.field_role is not None
                and len(reference_field.field_role) > 0
                else None
            )
            # If a link is in the form, we don't want to remove it.
            if (
                reference_field.field_type,
                ref_uid,
                ref_role,
            ) in action_object.reference_ids_to_remove:
                action_object.reference_ids_to_remove.remove(
                    (reference_field.field_type, ref_uid, ref_role)
                )
            # If a link is already in the requirement and traceability index,
            # there is nothing to do.
            if (
                reference_field.field_type,
                ref_uid,
                ref_role,
            ) in action_object.existing_references_uids:
                continue
            if reference_field.field_type == "Parent":
                traceability_index.update_requirement_parent_uid(
                    requirement=requirement,
                    parent_uid=ref_uid,
                    role=reference_field.field_role
                    if len(reference_field.field_role) > 0
                    else None,
                )
            elif reference_field.field_type == "Child":
                traceability_index.update_requirement_child_uid(
                    requirement=requirement,
                    child_uid=ref_uid,
                    role=reference_field.field_role
                    if len(reference_field.field_role) > 0
                    else None,
                )
            elif reference_field.field_type == "File":
                pass
            else:
                raise AssertionError(f"Must not reach here: {reference_field}")

        # Updating Traceability Index: UID
        traceability_index.update_requirement_uid(
            requirement=requirement, old_uid=existing_uid
        )

        # Calculate which documents and requirements have to be regenerated.
        for (
            _,
            reference_id_to_remove,
            _,
        ) in action_object.reference_ids_to_remove:
            removed_uid_parent_requirement = (
                traceability_index.graph_database.get_link_value(
                    link_type=GraphLinkType.UID_TO_REQUIREMENT_CONNECTIONS,
                    lhs_node=reference_id_to_remove,
                )
            )
            action_object.removed_uid_parent_documents_to_update.add(
                removed_uid_parent_requirement.document
            )
            # If a link was pointing towards a parent requirement in this
            # document, we will have to re-render it now.
            if removed_uid_parent_requirement.document == document:
                action_object.this_document_requirements_to_update.add(
                    removed_uid_parent_requirement.requirement
                )

        for (
            relation_type_,
            reference_id_to_remove,
            reference_id_to_remove_role,
        ) in action_object.reference_ids_to_remove:
            if relation_type_ == "Parent":
                traceability_index.remove_requirement_parent_uid(
                    requirement=requirement,
                    parent_uid=reference_id_to_remove,
                    role=reference_id_to_remove_role,
                )
            elif relation_type_ == "Child":
                traceability_index.remove_requirement_child_uid(
                    requirement=requirement,
                    child_uid=reference_id_to_remove,
                    role=reference_id_to_remove_role,
                )

        # Rendering back the Turbo template for each changed requirement.
        for reference_field in form_object.reference_fields:
            if reference_field.field_type not in ("Parent", "Child"):
                continue
            ref_uid = reference_field.field_value
            requirement_connections: SDocNodeConnections = (
                traceability_index.graph_database.get_link_value(
                    link_type=GraphLinkType.UID_TO_REQUIREMENT_CONNECTIONS,
                    lhs_node=ref_uid,
                )
            )

            if requirement_connections.document == document:
                action_object.this_document_requirements_to_update.add(
                    requirement_connections.requirement
                )

        traceability_index.update_last_updated()

        return UpdateRequirementResult(
            this_document_requirements_to_update=action_object.this_document_requirements_to_update
        )
