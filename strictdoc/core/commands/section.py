from collections import defaultdict
from typing import Dict, List, Optional, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.free_text import FreeText, FreeTextContainer
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.commands.constants import NodeCreationOrder
from strictdoc.core.commands.validation_error import (
    MultipleValidationError,
    SingleValidationError,
)
from strictdoc.core.traceability_index import (
    GraphLinkType,
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.section_form_object import (
    SectionFormObject,
)
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)


class UpdateSectionCommand:
    def __init__(
        self,
        form_object: SectionFormObject,
        section: Section,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: SectionFormObject = form_object
        self.section: Section = section
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        errors: Dict[str, List[str]] = defaultdict(list)
        validation_error = MultipleValidationError(
            "Section form has not passed validation.", errors
        )

        form_object = self.form_object
        section = self.section
        traceability_index = self.traceability_index

        if len(form_object.section_title) == 0:
            errors["section_title"].append("Section title must not be empty.")

        free_text_container: Optional[FreeTextContainer] = None
        if len(form_object.section_statement_unescaped) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter(
                context_document=section.document
            ).write_with_validation(form_object.section_statement_unescaped)
            if parsed_html is None:
                errors["section_statement"].append(rst_error)
            else:
                free_text_container = SDFreeTextReader.read(
                    form_object.section_statement_unescaped
                )
                anchors: List[Anchor] = []
                for part in free_text_container.parts:
                    if isinstance(part, InlineLink):
                        # FIXME: Add validations.
                        pass
                    elif isinstance(part, Anchor):
                        anchors.append(part)
                    else:
                        pass
                if anchors is not None:
                    try:
                        traceability_index.validate_node_against_anchors(
                            node=section, new_anchors=anchors
                        )
                    except SingleValidationError as anchors_validation_error:
                        errors["section_statement"].append(
                            anchors_validation_error.args[0]
                        )
        else:
            # If there is no free text, we need to check the anchors that may
            # have been in the existing free text.
            try:
                traceability_index.validate_node_against_anchors(
                    node=section, new_anchors=[]
                )
            except SingleValidationError as anchors_validation_error:
                errors["section_statement"].append(
                    anchors_validation_error.args[0]
                )
        if len(errors) > 0:
            raise validation_error

        # Updating section title.
        if (
            form_object.section_title is not None
            and len(form_object.section_title) > 0
        ):
            section.title = form_object.section_title
        else:
            assert "Should not reach here", form_object.section_title

        # Updating section content.
        if free_text_container is not None:
            existing_anchor_uids_to_remove = set()
            if len(section.free_texts) > 0:
                for part in section.free_texts[0].parts:
                    if isinstance(part, Anchor):
                        existing_anchor_uids_to_remove.add(part.value)

            if len(section.free_texts) > 0:
                free_text: FreeText = section.free_texts[0]
            else:
                free_text = FreeText(section, [])
                section.free_texts.append(free_text)
            free_text.parts = free_text_container.parts
            free_text.parent = section

            for part in free_text.parts:
                if isinstance(part, Anchor):
                    if part.value in existing_anchor_uids_to_remove:
                        existing_anchor_uids_to_remove.remove(part.value)
                    # By this time, we know that the validations have passed
                    # just before, so it is safe to update the anchor.
                    traceability_index.update_with_anchor(part)
                    part.parent = free_text
                elif isinstance(part, InlineLink):
                    part.parent = free_text

            for anchor_uid_to_be_removed in existing_anchor_uids_to_remove:
                anchor_uuid = next(
                    iter(
                        traceability_index.graph_database.get_link_values(
                            link_type=GraphLinkType.ANCHOR_UID_TO_ANCHOR_UUID,
                            lhs_node=anchor_uid_to_be_removed,
                        )
                    )
                )
                traceability_index.graph_database.remove_link(
                    link_type=GraphLinkType.ANCHOR_UID_TO_ANCHOR_UUID,
                    lhs_node=anchor_uid_to_be_removed,
                    rhs_node=anchor_uuid,
                )
                traceability_index.graph_database.remove_node(uuid=anchor_uuid)
        else:
            section.free_texts = []


class CreateSectionCommand:
    def __init__(
        self,
        form_object: SectionFormObject,
        whereto: str,
        reference_mid: str,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: SectionFormObject = form_object
        self.whereto: str = whereto
        self.reference_mid: str = reference_mid
        self.traceability_index: TraceabilityIndex = traceability_index

        self._created_section: Optional[Section] = None

    def get_created_section(self) -> Section:
        assert isinstance(self._created_section, Section)
        return self._created_section

    def perform(self):
        errors: Dict[str, List[str]] = defaultdict(list)
        validation_error = MultipleValidationError(
            "Section form has not passed validation.", errors
        )

        form_object = self.form_object
        whereto = self.whereto
        reference_mid = self.reference_mid
        traceability_index = self.traceability_index

        reference_node: Union[
            Document, Section
        ] = traceability_index.get_node_by_id(reference_mid)
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        if len(form_object.section_title) == 0:
            errors["section_title"].append("Section title must not be empty.")

        free_text_container: Optional[FreeTextContainer] = None
        if len(form_object.section_statement_unescaped) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter(
                context_document=document
            ).write_with_validation(form_object.section_statement_unescaped)
            if parsed_html is None:
                errors["section_statement"].append(rst_error)
            else:
                free_text_container = SDFreeTextReader.read(
                    form_object.section_statement_unescaped
                )
                anchors: List[Anchor] = []
                for part in free_text_container.parts:
                    if isinstance(part, InlineLink):
                        # FIXME: Add validations.
                        pass
                    elif isinstance(part, Anchor):
                        anchors.append(part)
                    else:
                        pass
                if anchors is not None:
                    try:
                        traceability_index.validate_node_against_anchors(
                            node=None, new_anchors=anchors
                        )
                    except SingleValidationError as anchors_validation_error:
                        errors["section_statement"].append(
                            anchors_validation_error.args[0]
                        )

        if len(errors) > 0:
            raise validation_error

        if whereto == NodeCreationOrder.CHILD:
            parent = reference_node
            insert_to_idx = len(parent.section_contents)
        elif whereto == NodeCreationOrder.BEFORE:
            assert isinstance(reference_node, (Requirement, Section))
            parent = reference_node.parent
            insert_to_idx = parent.section_contents.index(reference_node)
        elif whereto == NodeCreationOrder.AFTER:
            assert isinstance(reference_node, (Document, Requirement, Section))
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

        section = Section(
            parent=parent,
            uid=None,
            custom_level=None,
            title=None,
            requirement_prefix=None,
            free_texts=[],
            section_contents=[],
        )
        section.node_id = form_object.section_mid
        section.ng_document_reference = DocumentReference()
        section.ng_document_reference.set_document(document)
        assert parent.ng_level is not None, parent
        section.ng_level = parent.ng_level + 1
        traceability_index._map_id_to_node[section.node_id] = section
        parent.section_contents.insert(insert_to_idx, section)

        # Updating section title.
        if (
            form_object.section_title is not None
            and len(form_object.section_title) > 0
        ):
            section.title = form_object.section_title

        # Updating section content.
        if free_text_container is not None:
            if len(section.free_texts) > 0:
                free_text: FreeText = section.free_texts[0]
            else:
                free_text = FreeText(section, [])
                section.free_texts.append(free_text)
            free_text.parts = free_text_container.parts
            free_text.parent = section
            for part in free_text.parts:
                if isinstance(part, Anchor):
                    # Since this is a new section, we just need to register the
                    # new anchor. By this time, we know that there is no
                    # existing anchor with this name.
                    traceability_index.update_with_anchor(part)
                    part.parent = free_text
                elif isinstance(part, InlineLink):
                    part.parent = free_text
        else:
            section.free_texts = []

        self._created_section = section
