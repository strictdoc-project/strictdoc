from copy import copy
from dataclasses import dataclass
from typing import Optional, Set, Tuple, List

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.reference import (
    Reference,
    ParentReqReference,
    ChildReqReference,
)
from strictdoc.backend.sdoc.models.requirement import Requirement, \
    RequirementField
from strictdoc.backend.sdoc.models.type_system import RequirementFieldName
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex, \
    RequirementConnections
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
    RequirementReferenceFormField,
)


class UpdateRequirementActionObject:
    def __init__(self):
        self.existing_references_uids: Set[Tuple[str, Optional[str]]] = set()
        self.reference_ids_to_remove: Set[Tuple[str, Optional[str]]] = set()
        self.removed_uid_parent_documents_to_update: Set[Document] = set()
        # All requirements that have to be updated. This set includes
        # the requirement itself, all links it was linking to
        # (for deleted links) and all links it is linking to now
        # (including new links).
        self.this_document_requirements_to_update: Set[Requirement] = set()


@dataclass
class UpdateRequirementResult:
    this_document_requirements_to_update: Set[Requirement]


class UpdateRequirementCommand:
    def __init__(
        self,
        *,
        form_object: RequirementFormObject,
        requirement: Requirement,
        traceability_index: TraceabilityIndex,
        config: ProjectConfig,
    ):
        self.form_object: RequirementFormObject = form_object
        self.requirement: Requirement = requirement
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        form_object: RequirementFormObject = self.form_object
        requirement: Requirement = self.requirement
        document: Document = requirement.document
        traceability_index: TraceabilityIndex = self.traceability_index

        existing_uid: Optional[str] = requirement.reserved_uid

        # FIXME: [1] Leave only one method based on set_field_value().
        # Special case: we clear out the requirement's comments and then re-fill
        # them from scratch from the form data.
        if "COMMENT" in requirement.ordered_fields_lookup:
            del requirement.ordered_fields_lookup["COMMENT"]
        if RequirementFieldName.COMMENT in requirement.ng_reserved_fields_cache:
            del requirement.ng_reserved_fields_cache[
                RequirementFieldName.COMMENT
            ]

        for form_field_name, form_fields in form_object.fields.items():
            for form_field_index, form_field in enumerate(form_fields):
                requirement.set_field_value(
                    field_name=form_field_name,
                    form_field_index=form_field_index,
                    value=form_field.field_unescaped_value,
                )

        action_object = UpdateRequirementActionObject()
        action_object.existing_references_uids.update(
            requirement.get_parent_requirement_reference_uids()
        )
        action_object.reference_ids_to_remove = copy(
            action_object.existing_references_uids
        )
        action_object.this_document_requirements_to_update = {requirement}

        references: List[Reference] = []
        reference_field: RequirementReferenceFormField
        for reference_field in form_object.reference_fields:
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
            else:
                raise NotImplementedError(ref_type)
        if len(references) > 0:
            requirement.ordered_fields_lookup[RequirementFieldName.REFS] = [
                RequirementField(
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

        for (
            document_
        ) in traceability_index.document_tree.document_list:
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
            if (ref_uid, ref_role) in action_object.reference_ids_to_remove:
                action_object.reference_ids_to_remove.remove(
                    (ref_uid, ref_role)
                )
            # If a link is already in the requirement and traceability index,
            # there is nothing to do.
            if (ref_uid, ref_role) in action_object.existing_references_uids:
                continue
            traceability_index.update_requirement_parent_uid(
                requirement=requirement,
                parent_uid=ref_uid,
                role=reference_field.field_role,
            )

        # Updating Traceability Index: UID
        traceability_index.mut_rename_uid_to_a_requirement(
            requirement=requirement, old_uid=existing_uid
        )

        # Calculate which documents and requirements have to be regenerated.
        for reference_id_to_remove, _ in action_object.reference_ids_to_remove:
            removed_uid_parent_requirement = (
                traceability_index.requirements_connections[
                    reference_id_to_remove
                ]
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
            reference_id_to_remove,
            reference_id_to_remove_role,
        ) in action_object.reference_ids_to_remove:
            traceability_index.remove_requirement_parent_uid(
                requirement=requirement,
                parent_uid=reference_id_to_remove,
                role=reference_id_to_remove_role,
            )

        # Rendering back the Turbo template for each changed requirement.
        for reference_field in form_object.reference_fields:
            ref_uid = reference_field.field_value
            requirement_connections: RequirementConnections = (
                traceability_index.requirements_connections[
                    ref_uid
                ]
            )
            if requirement_connections.document == document:
                action_object.this_document_requirements_to_update.add(
                    requirement_connections.requirement
                )

        return UpdateRequirementResult(
            this_document_requirements_to_update=action_object.this_document_requirements_to_update
        )
