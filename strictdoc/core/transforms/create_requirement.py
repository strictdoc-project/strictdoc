from dataclasses import dataclass
from typing import List, Optional, Set, Tuple, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.core.transforms.constants import NodeCreationOrder
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
)
from strictdoc.helpers.mid import MID


class CreateRequirementActionObject:
    def __init__(self):
        self.existing_references_uids: Set[
            Tuple[str, str, Optional[str]]
        ] = set()
        self.reference_ids_to_remove: Set[
            Tuple[str, str, Optional[str]]
        ] = set()
        self.removed_uid_parent_documents_to_update: Set[Document] = set()
        # All requirements that have to be updated. This set includes
        # the requirement itself, all links it was linking to
        # (for deleted links) and all links it is linking to now
        # (including new links).
        self.this_document_requirements_to_update: Set[Requirement] = set()


@dataclass
class CreateRequirementResult:
    this_document_requirements_to_update: Set[Requirement]


class CreateRequirementTransform:
    def __init__(
        self,
        *,
        form_object: RequirementFormObject,
        whereto: str,
        requirement_mid: str,
        reference_mid: str,
        traceability_index: TraceabilityIndex,
    ):
        assert isinstance(reference_mid, str)
        self.form_object: RequirementFormObject = form_object
        self.whereto: str = whereto
        self.requirement_mid: str = requirement_mid
        self.reference_mid: str = reference_mid
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        form_object: RequirementFormObject = self.form_object
        whereto: str = self.whereto
        reference_mid: str = self.reference_mid
        traceability_index: TraceabilityIndex = self.traceability_index
        document: Document = traceability_index.get_node_by_mid(
            MID(form_object.document_mid)
        )
        reference_node: Union[
            Document, Section
        ] = traceability_index.get_node_by_mid(MID(reference_mid))

        if whereto == NodeCreationOrder.CHILD:
            parent = reference_node
            insert_to_idx = len(parent.section_contents)
        elif whereto == NodeCreationOrder.BEFORE:
            parent = reference_node.parent
            insert_to_idx = parent.section_contents.index(reference_node)
        elif whereto == NodeCreationOrder.AFTER:
            if isinstance(reference_node, Document):
                parent = reference_node
                insert_to_idx = 0
            else:
                parent = reference_node.parent
                insert_to_idx = (
                    parent.section_contents.index(reference_node) + 1
                )
        else:
            raise NotImplementedError

        # Reset the 'needs generation' flag on all documents.
        for document_ in traceability_index.document_tree.document_list:
            document_.ng_needs_generation = False

        requirement = SDocObjectFactory.create_requirement(parent=parent)

        # FIXME: Leave only one method based on set_field_value().
        for form_field_name, form_fields in form_object.fields.items():
            for form_field_index, form_field in enumerate(form_fields):
                requirement.set_field_value(
                    field_name=form_field_name,
                    form_field_index=form_field_index,
                    value=form_field.field_unescaped_value,
                )

        requirement.reserved_mid = MID(form_object.requirement_mid)
        if document.config.enable_mid:
            requirement.mid_permanent = True

        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(document)
        requirement.ng_level = parent.ng_level + 1
        parent.section_contents.insert(insert_to_idx, requirement)

        traceability_index.create_requirement(requirement=requirement)

        relations: List = form_object.get_requirement_relations(requirement)
        if len(relations) > 0:
            requirement.references = relations
            requirement.ordered_fields_lookup["REFS"] = [
                RequirementField(
                    parent=requirement,
                    field_name="REFS",
                    field_value=None,
                    field_value_multiline=None,
                    field_value_references=relations,
                )
            ]

        for relation_ in relations:
            if isinstance(relation_, ParentReqReference):
                traceability_index.update_requirement_parent_uid(
                    requirement, relation_.ref_uid, relation_.role
                )
            elif isinstance(relation_, ChildReqReference):
                traceability_index.update_requirement_child_uid(
                    requirement, relation_.ref_uid, relation_.role
                )
            else:
                # FIXME
                pass
