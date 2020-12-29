class DocumentReference:
    def __init__(self):
        self._document = None

    def get_document(self):
        return self._document

    def set_document(self, document):
        self._document = document
