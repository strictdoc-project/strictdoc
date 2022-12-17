import html
from typing import Optional

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.server.error_object import ErrorObject


class ExistingDocumentFreeTextObject(ErrorObject):
    def __init__(self, document_mid: str, document_free_text: Optional[str]):
        super().__init__()
        self.document_mid: str = document_mid
        if document_free_text is not None:
            document_free_text = html.escape(document_free_text)
        self._document_free_text: Optional[str] = document_free_text

    @property
    def document_free_text(self) -> str:
        if self._document_free_text is not None:
            assert len(self._document_free_text) > 0, self._document_free_text
            return self._document_free_text
        else:
            return ""

    @staticmethod
    def create_from_document(*, document: Document):
        if len(document.free_texts) == 0:
            return ExistingDocumentFreeTextObject(
                document_mid=document.node_id, document_free_text=None
            )
        document_free_text = ""
        for free_text in document.free_texts:
            document_free_text += free_text.get_parts_as_text()
        return ExistingDocumentFreeTextObject(
            document_mid=document.node_id, document_free_text=document_free_text
        )
