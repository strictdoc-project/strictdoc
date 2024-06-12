# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def"
from collections import defaultdict
from typing import Dict, List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.core.transforms.validation_error import (
    MultipleValidationError,
)
from strictdoc.export.html.form_objects.document_config_form_object import (
    DocumentConfigFormObject,
)


class UpdateDocumentConfigTransform:
    def __init__(
        self,
        form_object: DocumentConfigFormObject,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: DocumentConfigFormObject = form_object
        self.document: SDocDocument = document
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        form_object = self.form_object
        document = self.document

        try:
            self.validate(form_object, document)
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

    def validate(
        self,
        form_object: DocumentConfigFormObject,
        document: SDocDocument,
    ):
        errors: Dict[str, List[str]] = defaultdict(list)
        assert isinstance(document, SDocDocument)
        if len(form_object.document_title) == 0:
            errors["TITLE"].append("Document title must not be empty.")

        if len(errors):
            raise MultipleValidationError(
                "Document form has not passed validation.", errors=errors
            )
