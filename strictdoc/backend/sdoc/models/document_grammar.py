from collections import defaultdict, OrderedDict
from typing import List, Set, Dict

from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementField,
    GrammarElementFieldString,
)

RESERVED_NON_META_FIELDS = [
    "REFS",
    "TITLE",
    "STATEMENT",
    "COMMENT",
    "RATIONALE",
]


class GrammarElement:
    def __init__(self, parent, tag: str, fields: List[GrammarElementField]):
        self.parent = parent
        self.tag: str = tag
        self.fields: List[GrammarElementField] = fields
        fields_map: OrderedDict = OrderedDict()
        for field in fields:
            fields_map[field.title] = field
        self.fields_map = fields_map


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
            GrammarElementFieldString(
                parent=None, title="UID", required="False"
            ),
            GrammarElementFieldString(
                parent=None,
                title="LEVEL",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATUS",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None, title="TAGS", required="False"
            ),
            GrammarElementFieldString(
                parent=None, title="REFS", required="False"
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="RATIONALE",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="COMMENT",
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
