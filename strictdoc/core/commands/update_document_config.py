from collections import defaultdict
from typing import Dict, List, Optional

from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.free_text import FreeText, FreeTextContainer
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.core.commands.validation_error import (
    MultipleValidationError,
    SingleValidationError,
)
from strictdoc.core.traceability_index import (
    AnchorConnections,
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.document_config_form_object import (
    DocumentConfigFormObject,
)
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)


class UpdateDocumentConfigCommand:
    def __init__(
        self,
        form_object: DocumentConfigFormObject,
        document: Document,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: DocumentConfigFormObject = form_object
        self.document: Document = document
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        form_object = self.form_object
        document = self.document
        traceability_index = self.traceability_index

        try:
            self.validate(form_object, document, traceability_index)
        except MultipleValidationError:
            raise

        # Update the document.
        document.title = form_object.document_title
        document.config.uid = (
            form_object.document_uid
            if len(form_object.document_uid) > 0
            else None
        )
        document.config.version = (
            form_object.document_version
            if len(form_object.document_version) > 0
            else None
        )
        document.config.classification = (
            form_object.document_classification
            if len(form_object.document_classification) > 0
            else None
        )

        free_text: Optional[FreeText] = None
        if len(form_object.document_freetext_unescaped) > 0:
            free_text_container: FreeTextContainer = SDFreeTextReader.read(
                form_object.document_freetext_unescaped
            )
            free_text = FreeText(
                parent=document, parts=free_text_container.parts
            )
            free_text.parts = free_text_container.parts
            free_text.parent = document

            existing_anchor_uids_to_remove = set()
            if len(document.free_texts) > 0:
                for part in document.free_texts[0].parts:
                    if isinstance(part, Anchor):
                        existing_anchor_uids_to_remove.add(part.value)

            for part in free_text.parts:
                if isinstance(part, Anchor):
                    # We are simply rewriting the existing anchor if it exists,
                    # or we are creating a new one. By this time, we know that
                    # the validations have passed just before.
                    traceability_index.anchors_map[
                        part.value
                    ] = AnchorConnections(
                        anchor=part,
                        document=document,
                    )
                    part.parent = free_text
                elif isinstance(part, InlineLink):
                    part.parent = free_text

            for anchor_uid_to_be_removed in existing_anchor_uids_to_remove:
                del traceability_index.anchors_map[anchor_uid_to_be_removed]

        document.set_freetext(free_text)

    @staticmethod
    def validate(
        form_object: DocumentConfigFormObject,
        document: Document,
        traceability_index: TraceabilityIndex,
    ):
        errors: Dict[str, List[str]] = defaultdict(list)
        assert isinstance(document, Document)
        if len(form_object.document_title) == 0:
            errors["TITLE"].append("Document title must not be empty.")

        if len(form_object.document_freetext_unescaped) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter(
                context_document=document
            ).write_with_validation(form_object.document_freetext_unescaped)
            if parsed_html is None:
                errors["FREETEXT"].append(rst_error)

                free_text_container = SDFreeTextReader.read(
                    form_object.document_freetext_unescaped
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
                            node=document, new_anchors=anchors
                        )
                    except SingleValidationError as anchors_validation_error:
                        errors["FREETEXT"].append(
                            anchors_validation_error.args[0]
                        )

        if len(errors):
            raise MultipleValidationError(
                "Document form has not passed validation.", errors=errors
            )
