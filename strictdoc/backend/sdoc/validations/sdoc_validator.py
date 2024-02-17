from typing import Optional

from textx import get_location

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_view import DocumentView


class SDocValidator:
    """
    This helper class is used for validating SDoc documents right after the
    textX parsing and processing steps have finished.
    FIXME: In the future, all processing validation steps could be moved to this
           class as well. This would remove the need in the ParseContext class
           and simplify several other implementation details.
    """

    @staticmethod
    def validate_document(document: SDocDocument):
        SDocValidator._validate_document_config(document)
        SDocValidator._validate_document_view(document)

    @staticmethod
    def _validate_document_config(document: SDocDocument):
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

    @staticmethod
    def _validate_document_view(document: SDocDocument):
        document_view: Optional[DocumentView] = document.view
        if document_view is not None:
            for view in document_view.views:
                for tag in view.tags:
                    if (
                        tag.object_type
                        not in document.grammar.registered_elements
                    ):
                        raise StrictDocSemanticError.view_references_nonexisting_grammar_element(
                            view,
                            tag.object_type,
                            **get_location(document_view),
                        )
                    for field in tag.visible_fields:
                        for grammar_element in document.grammar.elements:
                            if field.name not in grammar_element.fields_map:
                                raise StrictDocSemanticError.view_references_nonexisting_field(
                                    view,
                                    tag.object_type,
                                    field.name,
                                    **get_location(document_view),
                                )
