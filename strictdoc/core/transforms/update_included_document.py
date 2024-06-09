# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from collections import defaultdict
from typing import Dict, List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.core.transforms.validation_error import (
    MultipleValidationError,
)
from strictdoc.export.html.form_objects.included_document_form_object import (
    IncludedDocumentFormObject,
)


class UpdateIncludedDocumentTransform:
    def __init__(
        self,
        form_object: IncludedDocumentFormObject,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
    ) -> None:
        self.form_object: IncludedDocumentFormObject = form_object
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

    def validate(
        self,
        form_object: IncludedDocumentFormObject,
        document: SDocDocument,
    ) -> None:
        errors: Dict[str, List[str]] = defaultdict(list)
        assert isinstance(document, SDocDocument)
        if len(form_object.document_title) == 0:
            errors["TITLE"].append("Document title must not be empty.")

        if len(errors):
            raise MultipleValidationError(
                "Document form has not passed validation.", errors=errors
            )
