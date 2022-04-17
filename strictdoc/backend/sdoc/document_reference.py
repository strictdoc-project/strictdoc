from typing import Optional

from strictdoc.backend.sdoc.models.document import Document


class DocumentReference:
    def __init__(self):
        self._document: Optional[Document] = None

    def get_document(self) -> Optional[Document]:
        return self._document

    def set_document(self, document):
        self._document = document
