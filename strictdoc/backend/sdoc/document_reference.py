# mypy: disable-error-code="no-untyped-def"
from typing import Optional

from strictdoc.backend.sdoc.models.document import SDocDocument


class DocumentReference:
    def __init__(self):
        self._document: Optional[SDocDocument] = None

    def get_document(self) -> Optional[SDocDocument]:
        return self._document

    def set_document(self, document):
        self._document = document
