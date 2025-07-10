"""
@relation(SDOC-SRS-55, scope=file)
"""

# mypy: disable-error-code="no-untyped-call,no-untyped-def,union-attr"
import datetime
from copy import copy
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union

from textx import TextXSyntaxError

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import get_textx_syntax_error_message
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.free_text import FreeTextContainer
from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.model import SDocDocumentIF, SDocSectionIF
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import (
    Reference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.constants import (
    GraphLinkType,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.core.transforms.constants import NodeCreationOrder
from strictdoc.core.transforms.validation_error import (
    SingleValidationError,
)
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormField,
    RequirementFormFieldType,
    RequirementFormObject,
)
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_modification_time import set_file_modification_time
from strictdoc.helpers.mid import MID


@dataclass
class CreateNodeInfo:
    whereto: str
    requirement_mid: str
    reference_mid: str


@dataclass
class UpdateNodeInfo:
    node_to_update: SDocNode


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
class CreateOrUpdateNodeResult:
    this_document_requirements_to_update: List[SDocNode]


class CreateOrUpdateNodeCommand:
    def __init__(
        self,
        *,
        form_object: RequirementFormObject,
        node_info: Union[CreateNodeInfo, UpdateNodeInfo],
        context_document: SDocDocument,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
    ) -> None:
        self.form_object: RequirementFormObject = form_object
        self.node_info: Union[CreateNodeInfo, UpdateNodeInfo] = node_info
        self.context_document: SDocDocument = context_document
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config

    def perform(self) -> Optional[CreateOrUpdateNodeResult]:
        form_object: RequirementFormObject = self.form_object
        node_to_update_or_none: Optional[SDocNode] = (
            self.node_info.node_to_update
            if isinstance(self.node_info, UpdateNodeInfo)
            else None
        )

        traceability_index: TraceabilityIndex = self.traceability_index

        map_form_to_requirement_fields: Dict[
            RequirementFormField, Optional[FreeTextContainer]
        ] = {}
        this_node_unique_anchors: Set[str] = set()
        for field_bucket_ in form_object.fields.values():
            field_: RequirementFormField
            for field_ in field_bucket_:
                if field_.field_type != RequirementFormFieldType.MULTILINE:
                    continue
                (
                    parsed_html,
                    rst_error,
                ) = RstToHtmlFragmentWriter(
                    project_config=self.project_config,
                    context_document=self.context_document,
                ).write_with_validation(field_.field_value)
                if parsed_html is None:
                    assert rst_error is not None
                    form_object.add_error(field_.field_name, rst_error)
                else:
                    try:
                        free_text_container: Optional[FreeTextContainer] = (
                            SDFreeTextReader.read(field_.field_value)
                            if len(field_.field_value) > 0
                            else None
                        )
                        map_form_to_requirement_fields[field_] = (
                            free_text_container
                        )
                        if free_text_container is None:
                            continue
                        anchors: List[Anchor] = []
                        for part in free_text_container.parts:
                            if isinstance(part, InlineLink):
                                linked_to_node = traceability_index.get_linkable_node_by_uid_weak(
                                    part.link
                                )
                                if linked_to_node is None:
                                    form_object.add_error(
                                        field_.field_name,
                                        "A LINK points to a node that does "
                                        f"not exist: '{part.link}'.",
                                    )
                            elif isinstance(part, Anchor):
                                if part.value in this_node_unique_anchors:
                                    form_object.add_error(
                                        field_.field_name,
                                        "The node fields contain duplicate anchor: "
                                        f"'{part.value}'.",
                                    )
                                    break
                                this_node_unique_anchors.add(part.value)
                                anchors.append(part)
                            else:
                                pass
                        if anchors is not None:
                            try:
                                traceability_index.validate_node_against_anchors(
                                    node=node_to_update_or_none,
                                    new_anchors=anchors,
                                )
                            except (
                                SingleValidationError
                            ) as anchors_validation_error:
                                form_object.add_error(
                                    field_.field_name,
                                    anchors_validation_error.args[0],
                                )
                    except TextXSyntaxError as exception:
                        form_object.add_error(
                            field_.field_name,
                            get_textx_syntax_error_message(exception),
                        )

        if form_object.any_errors():
            return None

        requirement: SDocNode
        document: SDocDocument
        existing_uid: Optional[str]
        existing_node_fields: List[SDocNodeField] = []
        if isinstance(self.node_info, UpdateNodeInfo):
            requirement = self.node_info.node_to_update
            document = assert_cast(requirement.get_document(), SDocDocument)

            existing_uid = requirement.reserved_uid

            existing_node_fields = list(requirement.enumerate_fields())

            # Clearing all existing fields because they will be recreated from
            # scratch from the form data.
            requirement.ordered_fields_lookup.clear()

            self.populate_node_fields_from_form_object(
                requirement, form_object, map_form_to_requirement_fields
            )

            # Updating Traceability Index: UID.
            traceability_index.update_requirement_uid(
                requirement=requirement, old_uid=existing_uid
            )
        else:
            reference_node: Union[SDocDocument, SDocSection] = (
                traceability_index.get_node_by_mid(
                    MID(self.node_info.reference_mid)
                )
            )
            document = traceability_index.get_node_by_mid(
                MID(form_object.document_mid)
            )
            parent: Union[SDocDocumentIF, SDocSectionIF]
            if self.node_info.whereto == NodeCreationOrder.CHILD:
                parent = reference_node
                insert_to_idx = len(parent.section_contents)
            elif self.node_info.whereto == NodeCreationOrder.BEFORE:
                # Be aware of an edge case besides all normal cases:
                # A reference node can be a root node of an included document.
                if not isinstance(reference_node, SDocDocument):
                    parent = reference_node.parent
                    insert_to_idx = parent.section_contents.index(
                        reference_node
                    )
                else:
                    parent = (
                        reference_node.ng_including_document_from_file.parent
                    )
                    assert (
                        reference_node.ng_including_document_from_file
                        is not None
                    )
                    insert_to_idx = parent.section_contents.index(
                        reference_node.ng_including_document_from_file
                    )
            elif self.node_info.whereto == NodeCreationOrder.AFTER:
                if isinstance(reference_node, SDocDocument):
                    assert reference_node.document_is_included()
                    parent = (
                        reference_node.ng_including_document_from_file.parent
                    )
                    assert reference_node.ng_including_document_from_file
                    insert_to_idx = (
                        parent.section_contents.index(
                            reference_node.ng_including_document_from_file
                        )
                        + 1
                    )
                else:
                    parent = reference_node.parent
                    insert_to_idx = (
                        parent.section_contents.index(reference_node) + 1
                    )
            else:
                raise NotImplementedError

            # Reset the 'needs generation' flag on all documents.
            for document_ in traceability_index.document_tree.document_list:
                set_file_modification_time(
                    document_.meta.input_doc_full_path,
                    datetime.datetime.today(),
                )

            # FIXME: It is better to have a general create_node method because
            #        we are dealing with arbitrary nodes, not only Requirement.
            requirement = SDocObjectFactory.create_requirement(
                parent=parent, node_type=form_object.element_type
            )
            requirement.reserved_mid = MID(form_object.requirement_mid)
            if document.config.enable_mid:
                requirement.mid_permanent = True

            grammar_element: GrammarElement = document.grammar.elements_by_type[
                form_object.element_type
            ]

            requirement.is_composite = (
                grammar_element.property_is_composite is True
            )
            requirement.ng_document_reference = DocumentReference()
            requirement.ng_document_reference.set_document(document)
            requirement.ng_including_document_reference = (
                document.ng_including_document_reference
            )

            parent.section_contents.insert(insert_to_idx, requirement)

            self.populate_node_fields_from_form_object(
                requirement, form_object, map_form_to_requirement_fields
            )
            traceability_index.create_requirement(requirement=requirement)

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
            requirement.relations = references
        else:
            requirement.relations = []

        for document_ in traceability_index.document_tree.document_list:
            set_file_modification_time(
                document_.meta.input_doc_full_path, datetime.datetime.today()
            )

        # Updating Traceability Index: Links.
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

        # Calculate which documents and requirements have to be regenerated.
        for (
            _,
            reference_id_to_remove,
            _,
        ) in action_object.reference_ids_to_remove:
            removed_uid_parent_requirement: SDocNode = (
                traceability_index.graph_database.get_link_value(
                    link_type=GraphLinkType.UID_TO_NODE,
                    lhs_node=reference_id_to_remove,
                )
            )
            removed_uid_parent_requirement_document = assert_cast(
                removed_uid_parent_requirement.get_document(), SDocDocument
            )
            action_object.removed_uid_parent_documents_to_update.add(
                removed_uid_parent_requirement_document
            )
            # If a link was pointing towards a parent requirement in this
            # document, we will have to re-render it now.
            if removed_uid_parent_requirement_document == document:
                action_object.this_document_requirements_to_update.add(
                    removed_uid_parent_requirement
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

            node: SDocNode = traceability_index.graph_database.get_link_value(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=ref_uid,
            )

            if node.get_document() == document:
                action_object.this_document_requirements_to_update.add(node)

        self._update_traceability_index_with_links_and_anchors(
            requirement, existing_node_fields
        )

        traceability_index.update_last_updated()

        return CreateOrUpdateNodeResult(
            this_document_requirements_to_update=list(
                action_object.this_document_requirements_to_update
            )
        )

    def _update_traceability_index_with_links_and_anchors(
        self, updated_node: SDocNode, existing_node_fields: List[SDocNodeField]
    ):
        traceability_index = self.traceability_index

        existing_anchor_uids: Set[str] = set()
        existing_links: List[InlineLink] = []
        for node_field_ in existing_node_fields:
            for part_ in node_field_.parts:
                if isinstance(part_, Anchor):
                    existing_anchor_uids.add(part_.value)
                elif isinstance(part_, InlineLink):
                    existing_links.append(part_)

        for existing_link_ in existing_links:
            traceability_index.remove_inline_link(existing_link_)

        for existing_anchor_uid in existing_anchor_uids:
            traceability_index.remove_anchor_by_uid(existing_anchor_uid)

        for node_field_ in updated_node.enumerate_fields():
            for part_ in node_field_.parts:
                if isinstance(part_, Anchor):
                    # Since this is a new section, we just need to register the
                    # new anchor. By this time, we know that there is no
                    # existing anchor with this name.
                    traceability_index.update_with_anchor(part_)
                elif isinstance(part_, InlineLink):
                    traceability_index.create_inline_link(part_)

    def populate_node_fields_from_form_object(
        self,
        node: SDocNode,
        form_object: RequirementFormObject,
        map_form_to_requirement_fields: Dict[
            RequirementFormField, Optional[FreeTextContainer]
        ],
    ):
        # FIXME: Leave only one method based on set_field_value().
        for form_field_name, form_fields in form_object.fields.items():
            for form_field_index, form_field in enumerate(form_fields):
                if form_field.field_type != RequirementFormFieldType.MULTILINE:
                    node.set_field_value(
                        field_name=form_field_name,
                        form_field_index=form_field_index,
                        value=form_field.field_value,
                    )
                    continue

                free_text_content: Optional[FreeTextContainer] = (
                    map_form_to_requirement_fields[form_field]
                )
                requirement_field = (
                    SDocNodeField(
                        node,
                        field_name=form_field_name,
                        parts=free_text_content.parts,
                        multiline__="true"
                        if form_field.field_type
                        == RequirementFormFieldType.MULTILINE
                        else None,
                    )
                    if free_text_content is not None
                    else None
                )
                node.set_field_value(
                    field_name=form_field_name,
                    form_field_index=form_field_index,
                    value=requirement_field,
                )
                if free_text_content is not None:
                    for part_ in requirement_field.parts:
                        if isinstance(part_, str):
                            continue
                        part_.parent = requirement_field
