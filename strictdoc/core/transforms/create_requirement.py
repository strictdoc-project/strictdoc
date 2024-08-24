# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def,union-attr,type-arg"
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union

from textx import TextXSyntaxError

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import get_textx_syntax_error_message
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.free_text import FreeTextContainer
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.core.transforms.constants import NodeCreationOrder
from strictdoc.core.transforms.validation_error import (
    MultipleValidationError,
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
from strictdoc.helpers.mid import MID


class CreateRequirementActionObject:
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
class CreateRequirementResult:
    this_document_requirements_to_update: Set[SDocNode]


class CreateRequirementTransform:
    def __init__(
        self,
        *,
        form_object: RequirementFormObject,
        project_config: ProjectConfig,
        whereto: str,
        requirement_mid: str,
        reference_mid: str,
        traceability_index: TraceabilityIndex,
    ):
        assert isinstance(reference_mid, str)
        self.form_object: RequirementFormObject = form_object
        self.project_config: ProjectConfig = project_config
        self.whereto: str = whereto
        self.requirement_mid: str = requirement_mid
        self.reference_mid: str = reference_mid
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        errors: Dict[str, List[str]] = defaultdict(list)
        validation_error = MultipleValidationError(
            "Node form has not passed validation.", errors
        )
        form_object: RequirementFormObject = self.form_object
        whereto: str = self.whereto
        reference_mid: str = self.reference_mid
        traceability_index: TraceabilityIndex = self.traceability_index
        document: SDocDocument = traceability_index.get_node_by_mid(
            MID(form_object.document_mid)
        )
        reference_node: Union[SDocDocument, SDocSection] = (
            traceability_index.get_node_by_mid(MID(reference_mid))
        )
        map_form_to_requirement_fields: Dict[
            RequirementFormField, Optional[FreeTextContainer]
        ] = {}
        for field_bucket_ in form_object.fields.values():
            field_: RequirementFormField
            for field_ in field_bucket_:
                if field_.field_type != RequirementFormFieldType.MULTILINE:
                    continue
                (
                    parsed_html,
                    rst_error,
                ) = RstToHtmlFragmentWriter(
                    path_to_output_dir=self.project_config.output_dir,
                    context_document=document,
                ).write_with_validation(field_.field_value)
                if parsed_html is None:
                    errors[field_.field_name].append(rst_error)
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
                                    errors[field_.field_name].append(
                                        "A LINK points to a node that does "
                                        f"not exist: '{part.link}'."
                                    )
                            elif isinstance(part, Anchor):
                                anchors.append(part)
                            else:
                                pass
                        if anchors is not None:
                            try:
                                traceability_index.validate_node_against_anchors(
                                    node=None, new_anchors=anchors
                                )
                            except (
                                SingleValidationError
                            ) as anchors_validation_error:
                                errors[field_.field_name].append(
                                    anchors_validation_error.args[0]
                                )
                    except TextXSyntaxError as exception:
                        errors[field_.field_name].append(
                            get_textx_syntax_error_message(exception)
                        )
        if len(errors) > 0:
            for field_name_, field_errors_ in validation_error.errors.items():
                for field_error_ in field_errors_:
                    form_object.add_error(field_name_, field_error_)
            return

        if whereto == NodeCreationOrder.CHILD:
            parent = reference_node
            insert_to_idx = len(parent.section_contents)
        elif whereto == NodeCreationOrder.BEFORE:
            # Be aware of an edge case besides all normal cases:
            # A reference node can be a root node of an included document.
            if not isinstance(reference_node, SDocDocument):
                parent = reference_node.parent
                insert_to_idx = parent.section_contents.index(reference_node)
            else:
                parent = reference_node.ng_including_document_from_file.parent
                insert_to_idx = parent.section_contents.index(
                    reference_node.ng_including_document_from_file
                )
        elif whereto == NodeCreationOrder.AFTER:
            if isinstance(reference_node, SDocDocument):
                assert reference_node.document_is_included()
                parent = reference_node.ng_including_document_from_file.parent
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
            document_.ng_needs_generation = False

        # FIXME: It is better to have a general create_node method because
        #        we are dealing with arbitrary nodes, not only Requirement.
        requirement = SDocObjectFactory.create_requirement(
            parent=parent, node_type=form_object.element_type
        )

        # FIXME: Leave only one method based on set_field_value().
        for form_field_name, form_fields in form_object.fields.items():
            for form_field_index, form_field in enumerate(form_fields):
                if form_field.field_type != RequirementFormFieldType.MULTILINE:
                    requirement.set_field_value(
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
                        requirement,
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
                requirement.set_field_value(
                    field_name=form_field_name,
                    form_field_index=form_field_index,
                    value=requirement_field,
                )
                if free_text_content is not None:
                    for part_ in requirement_field.parts:
                        if isinstance(part_, str):
                            continue
                        part_.parent = requirement_field

        requirement.reserved_mid = MID(form_object.requirement_mid)
        if document.config.enable_mid:
            requirement.mid_permanent = True

        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(document)
        requirement.ng_including_document_reference = (
            document.ng_including_document_reference
        )

        parent.section_contents.insert(insert_to_idx, requirement)

        traceability_index.create_requirement(requirement=requirement)

        relations: List = form_object.get_requirement_relations(requirement)
        if len(relations) > 0:
            requirement.relations = relations

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

        for free_text_container_ in map_form_to_requirement_fields.values():
            if free_text_container_ is None:
                continue
            for part in free_text_container_.parts:
                if isinstance(part, Anchor):
                    # Since this is a new section, we just need to register the
                    # new anchor. By this time, we know that there is no
                    # existing anchor with this name.
                    traceability_index.update_with_anchor(part)
                elif isinstance(part, InlineLink):
                    traceability_index.create_inline_link(part)

        traceability_index.update_last_updated()
