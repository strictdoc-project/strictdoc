from typing import Optional

from strictdoc.backend.sdoc.models.model import SDocDocumentIF


class DocumentReference:
    def __init__(self) -> None:
        self._document: Optional[SDocDocumentIF] = None

    def get_document(self) -> Optional[SDocDocumentIF]:
        return self._document

    def set_document(self, document: SDocDocumentIF) -> None:
        self._document = document
