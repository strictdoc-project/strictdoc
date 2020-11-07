from strictdoc.core.document_meta import DocumentMeta


class Document(object):
    def __init__(self, name, free_texts, section_contents):
        self.name = name
        self.free_texts = free_texts
        self.section_contents = section_contents

        self.ng_sections = []
        self.ng_level = 0
        self.meta = None

    def __str__(self):
        return "Document: <name: {}, section_contents: {}>".format(
            self.name, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    def assign_meta(self, meta):
        assert isinstance(meta, DocumentMeta)
        self.meta = meta
