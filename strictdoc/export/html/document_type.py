class DocumentType:
    DOCUMENT = 1
    TABLE = 2
    TRACE = 3
    DEEPTRACE = 4
    PDF = 5

    def __init__(self, document_type):
        self.document_type = document_type

    @staticmethod
    def all():
        return (
            DocumentType.DOCUMENT,
            DocumentType.TABLE,
            DocumentType.TRACE,
            DocumentType.DEEPTRACE,
            DocumentType.PDF,
        )

    @staticmethod
    def document():
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
    def is_document(self):
        return self.document_type == DocumentType.DOCUMENT

    @property
    def is_deeptrace(self):
        return self.document_type == DocumentType.DEEPTRACE
