from collections import defaultdict
from typing import List, Set, Dict

RESERVED_NON_META_FIELDS = [
    "REFS",
    "TITLE",
    "STATEMENT",
    "BODY",
    "COMMENT",
    "RATIONALE",
]


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
        self.parent = parent
        self.elements: List[GrammarElement] = elements

        registered_elements: Set[str] = set()
        elements_by_type: Dict[str, GrammarElement] = {}
        fields_by_type: Dict[str, Set[str]] = defaultdict(set)

        for element in elements:
            registered_elements.add(element.tag)
            elements_by_type[element.tag] = element
            for element_field in element.fields:
                fields_by_type[element.tag].add(element_field.title)

        self.registered_elements: Set[str] = registered_elements
        self.elements_by_type: Dict[str, GrammarElement] = elements_by_type
        self.fields_order_by_type: Dict[str, Set[str]] = fields_by_type

        self.is_default = False

    @staticmethod
    def create_default(parent):
        fields = [
            GrammarElementField(
                parent=None, title="UID", field_type="String", required="False"
            ),
            GrammarElementField(
                parent=None,
                title="LEVEL",
                field_type="String",
                required="False",
            ),
            GrammarElementField(
                parent=None,
                title="STATUS",
                field_type="String",
                required="False",
            ),
            GrammarElementField(
                parent=None, title="TAGS", field_type="String", required="False"
            ),
            GrammarElementField(
                parent=None,
                title="SPECIAL_FIELDS",
                field_type="String",
                required="False",
            ),
            GrammarElementField(
                parent=None, title="REFS", field_type="String", required="False"
            ),
            GrammarElementField(
                parent=None,
                title="TITLE",
                field_type="String",
                required="False",
            ),
            GrammarElementField(
                parent=None,
                title="STATEMENT",
                field_type="String",
                required="False",
            ),
            GrammarElementField(
                parent=None, title="BODY", field_type="String", required="False"
            ),
            GrammarElementField(
                parent=None,
                title="RATIONALE",
                field_type="String",
                required="False",
            ),
            GrammarElementField(
                parent=None,
                title="COMMENT",
                field_type="String",
                required="False",
            ),
        ]
        requirement_element = GrammarElement(
            parent=None, tag="REQUIREMENT", fields=fields
        )
        elements: List[GrammarElement] = [requirement_element]
        grammar = DocumentGrammar(parent=parent, elements=elements)
        grammar.is_default = True

        return grammar

    def dump_fields(self, requirement_type) -> str:
        return ", ".join(
            list(
                map(
                    lambda g: g.title,
                    self.elements_by_type[requirement_type].fields,
                )
            )
        )
