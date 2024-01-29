from textx import get_location

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig


class SDocValidator:
    """
    This helper class is used for validating SDoc documents right after the
    textX parsing and processing steps have finished.
    FIXME: In the future, all processing validation steps could be moved to this
           class as well. This would remove the need in the ParseContext class
           and simplify several other implementation details.
    """

    @staticmethod
    def validate_document(document: Document):
        SDocValidator._validate_document_config(document)

    @staticmethod
    def _validate_document_config(document: Document):
        document_config: DocumentConfig = document.config
        if document_config.default_view is not None:
            if document.view is None:
                raise StrictDocSemanticError.default_view_doesnt_exist(
                    document_config.default_view,
                    **get_location(document_config),
                )
            else:
                view_names = map(
                    lambda view_: view_.view_id, document.view.views
                )
                if document_config.default_view not in view_names:
                    raise StrictDocSemanticError.default_view_doesnt_exist(
                        document_config.default_view,
                        **get_location(document_config),
                    )
