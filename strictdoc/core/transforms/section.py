# mypy: disable-error-code="attr-defined,no-untyped-call,no-untyped-def,union-attr"
from collections import defaultdict
from typing import Dict, List, Optional, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode
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
from strictdoc.export.html.form_objects.section_form_object import (
    SectionFormObject,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID


class UpdateSectionCommand:
    def __init__(
        self,
        form_object: SectionFormObject,
        section: SDocSection,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: SectionFormObject = form_object
        self.section: SDocSection = section
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

        # Validate UID
        if section.reserved_uid is not None:
            # This is case where an existing section UID is being removed.
            # We have to check if this UID has incoming links to it, and if so,
            # raise a validation error.
            if len(form_object.section_uid) == 0:
                try:
                    traceability_index.validate_section_can_remove_uid(
                        section=section
                    )
                except SingleValidationError as validation_error_:
                    errors["section_uid"].append(validation_error_.args[0])
            else:
                if section.reserved_uid != form_object.section_uid:
                    section_incoming_links: Optional[List[InlineLink]] = (
                        traceability_index.get_incoming_links(section)
                    )
                    if (
                        section_incoming_links is not None
                        and len(section_incoming_links) > 0
                    ):
                        errors["section_uid"].append(
                            "Renaming a section UID when a section has "
                            "incoming links is not supported yet. "
                            "For now, please use a command-line process to "
                            "rename the section UID and all links that refer "
                            "to it."
                        )
        if len(form_object.section_uid) > 0:
            try:
                traceability_index.validate_can_create_uid(
                    form_object.section_uid, section.reserved_mid
                )
            except SingleValidationError as validation_error_:
                errors["section_uid"].append(validation_error_.args[0])

        if len(errors) > 0:
            raise validation_error

        # Updating section title.
        if (
            form_object.section_title is not None
            and len(form_object.section_title) > 0
        ):
            section.title = form_object.section_title
        else:
            raise AssertionError(
                f"Should not reach here: {form_object.section_title}"
            )

        # We have passed the validations if we reach this point, so we can
        # just assume we can safely delete the previous section UID
        # associations.
        traceability_index.delete_section(section)

        # Updating section UID.
        if len(form_object.section_uid) > 0:
            section_uid = assert_cast(form_object.section_uid, str)
            section.uid = section_uid
            section.reserved_uid = section_uid
        else:
            section.uid = None
            section.reserved_uid = None

        traceability_index.create_section(section)


class CreateSectionCommand:
    def __init__(
        self,
        form_object: SectionFormObject,
        whereto: str,
        reference_mid: str,
        traceability_index: TraceabilityIndex,
        config: ProjectConfig,
    ):
        self.form_object: SectionFormObject = form_object
        self.whereto: str = whereto
        self.reference_mid: str = reference_mid
        self.traceability_index: TraceabilityIndex = traceability_index
        self.config: ProjectConfig = config

        self._created_section: Optional[SDocSection] = None

    def get_created_section(self) -> SDocSection:
        assert isinstance(self._created_section, SDocSection)
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

        reference_node: Union[SDocDocument, SDocSection] = (
            traceability_index.get_node_by_mid(MID(reference_mid))
        )

        document: SDocDocument
        if isinstance(reference_node, SDocDocument):
            if not reference_node.document_is_included():
                document = reference_node
            else:
                # Edge case: a reference node is a root one from included document.
                # Only when a child node is added, the document is set to the included document.
                # Otherwise, to the including document.
                if whereto == "child":
                    document = reference_node
                else:
                    document = assert_cast(
                        reference_node.get_including_document(), SDocDocument
                    )
        else:
            document = reference_node.document

        if len(form_object.section_title) == 0:
            errors["section_title"].append("Section title must not be empty.")

        if len(
            form_object.section_uid
        ) > 0 and traceability_index.has_node_connections(
            form_object.section_uid
        ):
            existing_section = assert_cast(
                traceability_index.get_node_by_uid(form_object.section_uid),
                SDocSection,
            )
            errors["section_uid"].append(
                f"The chosen UID must be unique. "
                f"There is another section '{existing_section.title}' with "
                f"a UID '{form_object.section_uid}'."
            )

        if len(errors) > 0:
            raise validation_error

        if whereto == NodeCreationOrder.CHILD:
            parent = reference_node
            insert_to_idx = len(parent.section_contents)
        elif whereto == NodeCreationOrder.BEFORE:
            assert isinstance(
                reference_node, (SDocDocument, SDocNode, SDocSection)
            ), reference_node
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
            assert isinstance(
                reference_node, (SDocDocument, SDocNode, SDocSection)
            )
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

        section = SDocSection(
            parent=parent,
            mid=None,
            uid=None,
            custom_level=None,
            title="NOT_RELEVANT",
            requirement_prefix=None,
            free_texts=[],
            section_contents=[],
        )

        if len(form_object.section_uid) > 0:
            section_uid = assert_cast(form_object.section_uid, str)
            section.uid = section_uid
            section.reserved_uid = section_uid

        section.node_id = MID(form_object.section_mid)
        section.ng_document_reference = DocumentReference()
        section.ng_document_reference.set_document(document)
        section.ng_including_document_reference = (
            document.ng_including_document_reference
        )

        parent.section_contents.insert(insert_to_idx, section)

        traceability_index.create_section(section)

        # Updating section title.
        if (
            form_object.section_title is not None
            and len(form_object.section_title) > 0
        ):
            section.title = form_object.section_title

        self._created_section = section
