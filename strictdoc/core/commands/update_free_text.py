from typing import List, Optional, Union

from textx import TextXSyntaxError

from strictdoc.backend.sdoc.error_handling import get_textx_syntax_error_message
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.free_text import FreeText, FreeTextContainer
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.commands.validation_error import (
    SingleValidationError,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)


class UpdateFreeTextCommand:
    def __init__(
        self,
        node: Union[Document, Section],
        traceability_index: TraceabilityIndex,
        config: ProjectConfig,
        subject_field_name: str,
        subject_field_content: str,
    ):
        self.node: Union[Document, Section] = node
        self.traceability_index: TraceabilityIndex = traceability_index
        self.config: ProjectConfig = config
        self.subject_field_name: str = subject_field_name
        self.subject_field_content: str = subject_field_content

        self.validated_free_text_container: Optional[FreeTextContainer] = None

    def validate(self):
        node: Union[Document, Section] = self.node
        context_document = node if isinstance(node, Document) else node.document

        traceability_index = self.traceability_index
        subject_field_content = self.subject_field_content
        free_text_container: Optional[FreeTextContainer] = None

        if len(subject_field_content) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter(
                path_to_output_dir=self.config.export_output_dir,
                context_document=context_document,
            ).write_with_validation(subject_field_content)

            if parsed_html is None:
                raise SingleValidationError(rst_error)
            else:
                try:
                    free_text_container = SDFreeTextReader.read(
                        subject_field_content
                    )
                    anchors: List[Anchor] = []
                    for part in free_text_container.parts:
                        if isinstance(part, InlineLink):
                            linked_to_node = traceability_index.get_linkable_node_by_uid_weak(
                                part.link
                            )
                            if linked_to_node is None:
                                raise SingleValidationError(
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
                                node=node, new_anchors=anchors
                            )
                        except (
                            SingleValidationError
                        ) as anchors_validation_error:
                            raise SingleValidationError(
                                anchors_validation_error.args[0]
                            ) from None
                except TextXSyntaxError as exception:
                    raise SingleValidationError(
                        get_textx_syntax_error_message(exception)
                    ) from None
        else:
            # If there is no free text, we need to check the anchors that may
            # have been in the existing free text.
            try:
                traceability_index.validate_node_against_anchors(
                    node=node, new_anchors=[]
                )
            except SingleValidationError as anchors_validation_error:
                raise SingleValidationError(
                    anchors_validation_error.args[0]
                ) from None

        # Pass the optional validated to the perform command.
        self.validated_free_text_container = free_text_container

    def perform(self):
        node: Union[Document, Section] = self.node

        traceability_index = self.traceability_index

        # Updating section content.
        if self.validated_free_text_container is not None:
            free_text_container: FreeTextContainer = (
                self.validated_free_text_container
            )
            existing_links_to_remove: List[InlineLink] = []
            existing_anchor_uids_to_remove = set()
            if len(node.free_texts) > 0:
                for part in node.free_texts[0].parts:
                    if isinstance(part, Anchor):
                        existing_anchor_uids_to_remove.add(part.value)
                    elif isinstance(part, InlineLink):
                        existing_links_to_remove.append(part)

            if len(node.free_texts) > 0:
                free_text: FreeText = node.free_texts[0]
            else:
                free_text = FreeText(node, [])
                node.free_texts.append(free_text)
            free_text.parts = free_text_container.parts
            free_text.parent = node

            new_links_to_add: List[InlineLink] = []
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
                    new_links_to_add.append(part)

            for anchor_uid_to_be_removed in existing_anchor_uids_to_remove:
                anchor = traceability_index.graph_database.get_node_by_uid(
                    anchor_uid_to_be_removed
                )
                traceability_index.graph_database.remove_node_by_mid(anchor.mid)

            for existing_link in existing_links_to_remove:
                traceability_index.remove_inline_link(existing_link)
            for new_link in new_links_to_add:
                traceability_index.create_inline_link(new_link)
        else:
            existing_links_to_remove = []
            if len(node.free_texts) > 0:
                for part in node.free_texts[0].parts:
                    if isinstance(part, InlineLink):
                        existing_links_to_remove.append(part)
            for existing_link in existing_links_to_remove:
                traceability_index.remove_inline_link(existing_link)
            node.free_texts = []
