from enum import Enum
from typing import Tuple


class DocumentType(str, Enum):
    DOCUMENT = "DOCUMENT"
    TABLE = "TABLE"
    TRACE = "TRACE"
    DEEPTRACE = "DEEPTRACE"
    PDF = "PDF"

    @staticmethod
    def all() -> Tuple["DocumentType", ...]:  # noqa: A003
        return (
            DocumentType.DOCUMENT,
            DocumentType.TABLE,
            DocumentType.TRACE,
            DocumentType.DEEPTRACE,
            DocumentType.PDF,
        )

    def is_document(self) -> bool:
        return self == DocumentType.DOCUMENT

    def is_table(self) -> bool:
        return self == DocumentType.TABLE

    def is_trace(self) -> bool:
        return self == DocumentType.TRACE

    def is_deeptrace(self) -> bool:
        return self == DocumentType.DEEPTRACE

    def is_pdf(self) -> bool:
        return self == DocumentType.PDF

    def get_page_title(self) -> str:
        if self == DocumentType.DOCUMENT:
            return "Document"
        if self == DocumentType.TABLE:
            return "Table"
        if self == DocumentType.TRACE:
            return "Traceability"
        if self == DocumentType.DEEPTRACE:
            return "Deep Traceability"
        if self == DocumentType.PDF:
            return "PDF"
        raise NotImplementedError
