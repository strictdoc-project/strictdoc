# mypy: disable-error-code="no-untyped-call,no-untyped-def"
# FIXME: Migrate this to a proper Enum.
class DocumentType:
    DOCUMENT = "document"
    TABLE = "table"
    TRACE = "trace"
    DEEPTRACE = "deeptrace"
    PDF = "pdf"

    def __init__(self, document_type: str):
        self.document_type: str = document_type

    @staticmethod
    def all():  # noqa: A003
        return (
            DocumentType.DOCUMENT,
            DocumentType.TABLE,
            DocumentType.TRACE,
            DocumentType.DEEPTRACE,
            DocumentType.PDF,
        )

    @staticmethod
    def document() -> "DocumentType":
        return DocumentType(DocumentType.DOCUMENT)

    @staticmethod
    def table():
        return DocumentType(DocumentType.TABLE)

    @staticmethod
    def trace():
        return DocumentType(DocumentType.TRACE)

    @staticmethod
    def deeptrace():
        return DocumentType(DocumentType.DEEPTRACE)

    @staticmethod
    def pdf():
        return DocumentType(DocumentType.PDF)

    @property
    def is_document(self) -> bool:
        return self.document_type == DocumentType.DOCUMENT

    def is_table(self) -> bool:
        return self.document_type == DocumentType.TABLE

    def is_trace(self) -> bool:
        return self.document_type == DocumentType.TRACE

    @property
    def is_deeptrace(self) -> bool:
        return self.document_type == DocumentType.DEEPTRACE

    def is_pdf(self) -> bool:
        return self.document_type == DocumentType.PDF

    def get_page_title(self) -> str:
        if self.document_type == DocumentType.DOCUMENT:
            return "Document"
        if self.document_type == DocumentType.TABLE:
            return "Table"
        if self.document_type == DocumentType.TRACE:
            return "Traceability"
        if self.document_type == DocumentType.DEEPTRACE:
            return "Deep Traceability"
        if self.document_type == DocumentType.PDF:
            return "PDF"
        raise NotImplementedError  # pragma: no cover
