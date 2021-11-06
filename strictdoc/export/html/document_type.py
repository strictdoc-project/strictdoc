class DocumentType:
    DOCUMENT = 1
    TABLE = 2
    TRACE = 3
    DEEPTRACE = 4

    def __init__(self, document_type):
        self.document_type = document_type

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

    @property
    def is_deeptrace(self):
        return self.document_type == DocumentType.DEEPTRACE
