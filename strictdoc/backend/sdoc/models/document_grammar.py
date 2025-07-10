# mypy: disable-error-code="no-untyped-call,union-attr"
from typing import Dict, List, Optional, Set, Union

from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
)
from strictdoc.backend.sdoc.models.model import (
    RequirementFieldName,
    SDocDocumentIF,
    SDocGrammarIF,
)


class DocumentGrammar(SDocGrammarIF):
    def __init__(
        self,
        parent: Optional[SDocDocumentIF],
        elements: List[GrammarElement],
        import_from_file: Optional[str] = None,
    ) -> None:
        self.parent: Optional[SDocDocumentIF] = parent
        self.elements: List[GrammarElement] = elements

        self.registered_elements: Set[str] = set()
        self.elements_by_type: Dict[str, GrammarElement] = {}

        self.update_with_elements(elements)

        # The textX parser passes an empty string instead of None when
        # import_from_file is not provided in input.
        if import_from_file is not None and len(import_from_file) == 0:
            import_from_file = None
        self.import_from_file: Optional[str] = import_from_file

        self.is_default = False

        self.ng_line_start: Optional[int] = None
        self.ng_col_start: Optional[int] = None

    @staticmethod
    def create_default(
        parent: Optional[SDocDocumentIF],
        create_section_element: bool = False,
        enable_mid: bool = False,
    ) -> "DocumentGrammar":
        text_element: GrammarElement = (
            DocumentGrammar.create_default_text_element(enable_mid=enable_mid)
        )

        # @relation(SDOC-SRS-132, scope=range_start)
        fields: List[
            Union[
                GrammarElementFieldString,
                GrammarElementFieldSingleChoice,
                GrammarElementFieldMultipleChoice,
            ]
        ] = []

        if enable_mid:
            fields.append(
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.MID,
                    human_title=None,
                    required="False",
                )
            )

        fields.extend(
            [
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.UID,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.LEVEL,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.STATUS,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.TAGS,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.TITLE,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.STATEMENT,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.RATIONALE,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.COMMENT,
                    human_title=None,
                    required="False",
                ),
            ]
        )

        requirement_element = GrammarElement(
            parent=None,
            tag="REQUIREMENT",
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[],
        )
        # @relation(SDOC-SRS-132, scope=range_end)

        requirement_element.relations = GrammarElement.create_default_relations(
            requirement_element
        )

        elements: List[GrammarElement] = []

        if create_section_element:
            section_element: GrammarElement = (
                DocumentGrammar.create_default_section_element(
                    enable_mid=enable_mid
                )
            )
            elements.append(section_element)

        elements.append(text_element)
        elements.append(requirement_element)

        grammar = DocumentGrammar(
            parent=parent, elements=elements, import_from_file=None
        )
        grammar.is_default = True
        text_element.parent = grammar
        requirement_element.parent = grammar

        return grammar

    @staticmethod
    def create_for_test_report(parent: SDocDocumentIF) -> "DocumentGrammar":
        text_element: GrammarElement = (
            DocumentGrammar.create_default_text_element()
        )

        fields: List[
            Union[
                GrammarElementFieldString,
                GrammarElementFieldSingleChoice,
                GrammarElementFieldMultipleChoice,
            ]
        ] = [
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.UID,
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TEST_PATH",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TEST_FUNCTION",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="DURATION",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.STATUS,
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.TITLE,
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.STATEMENT,
                human_title=None,
                required="False",
            ),
        ]
        requirement_element = GrammarElement(
            parent=None,
            tag="TEST_RESULT",
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[],
        )

        requirement_element.relations = GrammarElement.create_default_relations(
            requirement_element
        )

        elements: List[GrammarElement] = [text_element, requirement_element]
        grammar = DocumentGrammar(
            parent=parent, elements=elements, import_from_file=None
        )
        grammar.is_default = True
        text_element.parent = grammar
        requirement_element.parent = grammar

        return grammar

    def get_element_by_mid(self, element_mid: str) -> GrammarElement:
        for element_ in self.elements:
            if element_.mid == element_mid:
                return element_
        raise AssertionError(
            f"Could not find a grammar element with MID: {element_mid}"
        )

    def dump_fields(self, node_type: str) -> str:
        return ", ".join(
            list(
                map(
                    lambda g: g.title,
                    self.elements_by_type[node_type].fields,
                )
            )
        )

    def has_text_element(self) -> bool:
        for element_ in self.elements:
            if element_.tag == "TEXT":
                return True
        return False

    def add_element_first(self, element: GrammarElement) -> None:
        self.elements.insert(0, element)
        self.elements_by_type[element.tag] = element
        self.registered_elements.add(element.tag)
        self.is_default = False

    def update_element(
        self, existing_element: GrammarElement, updated_element: GrammarElement
    ) -> None:
        element_index = self.elements.index(existing_element)
        self.elements[element_index] = updated_element
        self.elements_by_type[updated_element.tag] = updated_element
        self.is_default = False

    def update_with_elements(self, elements: List[GrammarElement]) -> None:
        # When elements are created by code, not by textX, it is convenient
        # if their .parent is set here automatically.
        for element_ in elements:
            element_.parent = self

        registered_elements: Set[str] = set()
        elements_by_type: Dict[str, GrammarElement] = {}
        for element in elements:
            registered_elements.add(element.tag)
            elements_by_type[element.tag] = element

        self.elements = elements
        self.registered_elements = registered_elements
        self.elements_by_type = elements_by_type

    @staticmethod
    def create_default_text_element(
        parent: Optional["DocumentGrammar"] = None,
        enable_mid: bool = False,
    ) -> GrammarElement:
        fields: List[
            Union[
                GrammarElementFieldString,
                GrammarElementFieldSingleChoice,
                GrammarElementFieldMultipleChoice,
            ]
        ] = []
        if enable_mid:
            fields.append(
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.MID,
                    human_title=None,
                    required="False",
                )
            )
        fields.extend(
            [
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.UID,
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.STATEMENT,
                    human_title=None,
                    required="True",
                ),
            ]
        )
        text_element = GrammarElement(
            parent=parent,
            tag="TEXT",
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[],
        )
        return text_element

    @staticmethod
    def create_default_section_element(
        parent: Optional["DocumentGrammar"] = None, enable_mid: bool = False
    ) -> GrammarElement:
        fields: List[
            Union[
                GrammarElementFieldString,
                GrammarElementFieldSingleChoice,
                GrammarElementFieldMultipleChoice,
            ]
        ] = []
        if enable_mid:
            fields.append(
                GrammarElementFieldString(
                    parent=None,
                    title=RequirementFieldName.MID,
                    human_title=None,
                    required="True",
                )
            )
        fields.append(
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.UID,
                human_title=None,
                required="False",
            )
        )
        fields.append(
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.LEVEL,
                human_title=None,
                required="False",
            )
        )
        fields.append(
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.PREFIX,
                human_title=None,
                required="False",
            )
        )
        fields.append(
            GrammarElementFieldString(
                parent=None,
                title=RequirementFieldName.TITLE,
                human_title=None,
                required="True",
            ),
        )
        section_element = GrammarElement(
            parent=parent,
            tag="SECTION",
            property_is_composite="True",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[],
        )
        return section_element


class DocumentGrammarWrapper:
    def __init__(self, grammar: DocumentGrammar):
        assert isinstance(grammar, DocumentGrammar), grammar
        self.grammar: DocumentGrammar = grammar
