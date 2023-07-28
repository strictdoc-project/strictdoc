from collections import defaultdict
from typing import Dict, List, Optional, Union

from textx import TextXSyntaxError

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import get_textx_syntax_error_message
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.free_text import FreeText, FreeTextContainer
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.commands.constants import NodeCreationOrder
from strictdoc.core.commands.update_free_text import UpdateFreeTextCommand
from strictdoc.core.commands.validation_error import (
    MultipleValidationError,
    SingleValidationError,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    RequirementConnections,
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.section_form_object import (
    SectionFormObject,
)
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID


class UpdateSectionCommand:
    def __init__(
        self,
        form_object: SectionFormObject,
        section: Section,
        traceability_index: TraceabilityIndex,
        config: ProjectConfig,
    ):
        self.form_object: SectionFormObject = form_object
        self.section: Section = section
        self.traceability_index: TraceabilityIndex = traceability_index
        self.update_free_text_command = UpdateFreeTextCommand(
            node=section,
            traceability_index=traceability_index,
            config=config,
            subject_field_name="section_statement",
            subject_field_content=form_object.section_statement_unescaped,
        )

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
                    section_incoming_links: Optional[
                        List[InlineLink]
                    ] = traceability_index.get_section_incoming_links(section)
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
                    form_object.section_uid
                )
            except SingleValidationError as validation_error_:
                errors["section_uid"].append(validation_error_.args[0])

        try:
            self.update_free_text_command.validate()
        except SingleValidationError as free_text_validation_error:
            errors["section_statement"].append(
                free_text_validation_error.args[0]
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

        # Updating section UID.
        if len(form_object.section_uid) > 0:
            # We have passed the validations if we reach this point, so we can
            # just assume we can safely delete the previous section UID
            # associations.
            if section.reserved_uid is not None:
                del traceability_index.requirements_parents[
                    section.reserved_uid
                ]

            section.uid = form_object.section_uid
            section.reserved_uid = form_object.section_uid
            traceability_index.requirements_parents[
                section.reserved_uid
            ] = RequirementConnections(
                requirement=section,
                document=section.document,
                parents=[],
                parents_uids=[],
                children=[],
            )
        else:
            # We have passed the validations if we reach this point, so we can
            # just assume we can safely delete the section.
            if section.reserved_uid is not None:
                del traceability_index.requirements_parents[
                    section.reserved_uid
                ]
                section.uid = None
                section.reserved_uid = None

        # Updating section content.
        self.update_free_text_command.perform()


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
        ] = traceability_index.get_node_by_mid(MID(reference_mid))
        document = (
            reference_node
            if isinstance(reference_node, Document)
            else reference_node.document
        )

        if len(form_object.section_title) == 0:
            errors["section_title"].append("Section title must not be empty.")

        if (
            len(form_object.section_uid) > 0
            and form_object.section_uid
            in traceability_index.requirements_parents
        ):
            existing_section_connections: RequirementConnections = assert_cast(
                traceability_index.requirements_parents[
                    form_object.section_uid
                ],
                RequirementConnections,
            )
            existing_section = assert_cast(
                existing_section_connections.requirement, Section
            )
            errors["section_uid"].append(
                f"The chosen UID must be unique. "
                f"There is another section '{existing_section.title}' with "
                f"a UID '{form_object.section_uid}'."
            )

        free_text_container: Optional[FreeTextContainer] = None
        if len(form_object.section_statement_unescaped) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter(
                path_to_output_dir=self.config.export_output_dir,
                context_document=document,
            ).write_with_validation(form_object.section_statement_unescaped)
            if parsed_html is None:
                errors["section_statement"].append(rst_error)
            else:
                try:
                    free_text_container = SDFreeTextReader.read(
                        form_object.section_statement_unescaped
                    )
                    anchors: List[Anchor] = []
                    for part in free_text_container.parts:
                        if isinstance(part, InlineLink):
                            linked_to_node = traceability_index.get_linkable_node_by_uid_weak(
                                part.link
                            )
                            if linked_to_node is None:
                                errors["section_statement"].append(
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
                            errors["section_statement"].append(
                                anchors_validation_error.args[0]
                            )
                except TextXSyntaxError as exception:
                    errors["section_statement"].append(
                        get_textx_syntax_error_message(exception)
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

        if len(form_object.section_uid) > 0:
            section.uid = form_object.section_uid
            section.reserved_uid = form_object.section_uid
            traceability_index.requirements_parents[
                section.reserved_uid
            ] = RequirementConnections(
                requirement=section,
                document=document,
                parents=[],
                parents_uids=[],
                children=[],
            )

        section.node_id = MID(form_object.section_mid)
        section.ng_document_reference = DocumentReference()
        section.ng_document_reference.set_document(document)
        assert parent.ng_level is not None, parent
        section.ng_level = parent.ng_level + 1
        traceability_index._map_id_to_node[section.mid] = section
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
