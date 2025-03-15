from typing import Optional

from strictdoc.backend.sdoc.models.document import SDocDocument


class DocumentReference:
    def __init__(self) -> None:
        self._document: Optional[SDocDocument] = None

    def get_document(self) -> Optional[SDocDocument]:
        return self._document

    def set_document(self, document: SDocDocument) -> None:
        self._document = document
