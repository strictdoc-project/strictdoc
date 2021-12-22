from typing import List

from strictdoc.backend.dsl.models.document import Document


class GrammarElementField:
    def __init__(self, parent, title: str, field_type: str, required: str):
        self.parent = parent
        self.title: str = title
        self.field_type: str = field_type
        self.required: bool = required == "True"


class GrammarElement:
    def __init__(self, parent, tag: str, fields: List[GrammarElementField]):
        self.parent = parent
        self.tag: str = tag
        self.fields: List[GrammarElementField] = fields


class DocumentGrammar:
    def __init__(self, parent, elements: List[GrammarElement]):
        assert isinstance(parent, Document)
        self.parent: Document = parent
        self.elements: List[GrammarElement] = elements
