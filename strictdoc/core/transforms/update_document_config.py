"""
@relation(SDOC-SRS-57, scope=file)
"""

import re
from collections import defaultdict
from typing import Dict, List, Optional

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import (
    DocumentCustomMetadata,
    DocumentCustomMetadataKeyValuePair,
)
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.core.transforms.validation_error import (
    MultipleValidationError,
)
from strictdoc.export.html.form_objects.document_config_form_object import (
    DocumentConfigFormObject,
)

DOCUMENT_CUSTOM_METADATA_KEY_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_-]*")


class UpdateDocumentConfigTransform:
    def __init__(
        self,
        form_object: DocumentConfigFormObject,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
    ) -> None:
        self.form_object: DocumentConfigFormObject = form_object
        self.document: SDocDocument = document
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self) -> None:
        form_object = self.form_object
        document = self.document

        try:
            self.validate(form_object, document)
        except MultipleValidationError:
            raise

        # Update the document.
        document.title = form_object.document_title
        document.config.version = (
            form_object.document_version
            if form_object.document_version is not None
            and len(form_object.document_version) > 0
            else None
        )
        document.config.classification = (
            form_object.document_classification
            if form_object.document_classification is not None
            and len(form_object.document_classification) > 0
            else None
        )
        document.config.requirement_prefix = (
            form_object.document_requirement_prefix
            if form_object.document_requirement_prefix is not None
            and len(form_object.document_requirement_prefix) > 0
            else None
        )
        if len(form_object.custom_metadata_fields):
            entries = [
                DocumentCustomMetadataKeyValuePair(
                    key=field.field_name, value=field.field_value
                )
                for field in form_object.custom_metadata_fields
            ]
            document.config.custom_metadata = DocumentCustomMetadata(
                entries=entries
            )
        else:
            document.config.custom_metadata = None

        self.traceability_index.delete_document(document)

        document.config.uid = (
            form_object.document_uid
            if form_object.document_uid is not None
            and len(form_object.document_uid) > 0
            else None
        )

        self.traceability_index.create_document(document)

    def validate(
        self,
        form_object: DocumentConfigFormObject,
        document: SDocDocument,
    ) -> None:
        errors: Dict[str, List[str]] = defaultdict(list)
        assert isinstance(document, SDocDocument)

        if len(form_object.document_title) == 0:
            errors["TITLE"].append("Document title must not be empty.")

        # Ensure that UID doesn't have any incoming links if it is going to be
        # renamed or removed.
        existing_uid = document.reserved_uid
        new_uid = form_object.document_uid
        if existing_uid is not None:
            if new_uid is None or existing_uid != new_uid:
                existing_incoming_links: Optional[List[InlineLink]] = (
                    self.traceability_index.get_incoming_links(document)
                )
                if (
                    existing_incoming_links is not None
                    and len(existing_incoming_links) > 0
                ):
                    errors["UID"].append(
                        (
                            "Renaming a node UID when the node has "
                            "incoming links is not supported yet. "
                            "Please delete all incoming links first."
                        ),
                    )

        for metadata_field in form_object.custom_metadata_fields:
            metadata_error_key = f"METADATA[{metadata_field.field_mid}]"
            if len(metadata_field.field_name) == 0:
                errors[metadata_error_key].append("Key must not be empty.")
            elif (
                DOCUMENT_CUSTOM_METADATA_KEY_RE.fullmatch(
                    metadata_field.field_name
                )
                is None
            ):
                # Keep this validation aligned with DocumentCustomMetadataKey
                # in the SDOC grammar so saved documents remain parseable.
                errors[metadata_error_key].append(
                    "Key must start with an ASCII letter or underscore and "
                    "contain only ASCII letters, digits, underscores, or "
                    "hyphens."
                )
            if len(metadata_field.field_value) == 0:
                errors[metadata_error_key].append("Value must not be empty.")

        if len(errors):
            raise MultipleValidationError(
                "Document form has not passed validation.", errors=errors
            )
