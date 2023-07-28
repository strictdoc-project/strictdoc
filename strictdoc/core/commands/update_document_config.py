from collections import defaultdict
from typing import Dict, List

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.core.commands.update_free_text import UpdateFreeTextCommand
from strictdoc.core.commands.validation_error import (
    MultipleValidationError,
    SingleValidationError,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.document_config_form_object import (
    DocumentConfigFormObject,
)


class UpdateDocumentConfigCommand:
    def __init__(
        self,
        form_object: DocumentConfigFormObject,
        document: Document,
        traceability_index: TraceabilityIndex,
        config: ProjectConfig,
    ):
        self.form_object: DocumentConfigFormObject = form_object
        self.document: Document = document
        self.traceability_index: TraceabilityIndex = traceability_index
        self.update_free_text_command = UpdateFreeTextCommand(
            node=document,
            traceability_index=traceability_index,
            config=config,
            subject_field_name="FREETEXT",
            subject_field_content=form_object.document_freetext_unescaped,
        )

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

        self.update_free_text_command.perform()

    def validate(
        self,
        form_object: DocumentConfigFormObject,
        document: Document,
    ):
        errors: Dict[str, List[str]] = defaultdict(list)
        assert isinstance(document, Document)
        if len(form_object.document_title) == 0:
            errors["TITLE"].append("Document title must not be empty.")

        try:
            self.update_free_text_command.validate()
        except SingleValidationError as free_text_validation_error:
            errors["FREETEXT"].append(free_text_validation_error.args[0])

        if len(errors):
            raise MultipleValidationError(
                "Document form has not passed validation.", errors=errors
            )
