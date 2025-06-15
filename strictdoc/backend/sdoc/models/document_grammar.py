# mypy: disable-error-code="no-untyped-call,union-attr"
from collections import OrderedDict
from typing import Dict, Generator, List, Optional, Set, Tuple, Union

from strictdoc.backend.sdoc.models.model import SDocDocumentIF, SDocGrammarIF
from strictdoc.backend.sdoc.models.type_system import (
    RESERVED_NON_META_FIELDS,
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    GrammarElementRelationParent,
    RequirementFieldName,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.mid import MID


@auto_described()
class GrammarElement:
    def __init__(
        self,
        parent: Optional["DocumentGrammar"],
        tag: str,
        property_is_composite: str,
        property_prefix: str,
        property_view_style: str,
        fields: List[
            Union[
                GrammarElementFieldString,
                GrammarElementFieldMultipleChoice,
                GrammarElementFieldSingleChoice,
            ]
        ],
        relations: List[
            Union[
                GrammarElementRelationParent,
                GrammarElementRelationChild,
                GrammarElementRelationFile,
            ]
        ],
    ) -> None:
        self.parent: Optional[DocumentGrammar] = parent
        self.tag: str = tag

        assert property_is_composite in ("", "True", "False")
        self.property_is_composite: Optional[bool] = (
            None
            if property_is_composite == ""
            else (property_is_composite == "True")
        )

        self.property_prefix: Optional[str] = (
            property_prefix if property_prefix not in (None, "") else None
        )

        assert property_view_style in (
            "",
            "Plain",
            "Narrative",
            "Simple",
            "Inline",
            "Table",
            "Zebra",
        )
        self.property_view_style: Optional[str] = (
            property_view_style if property_view_style != "" else None
        )
        self.property_view_style_lower: Optional[str] = (
            property_view_style.lower() if property_view_style != "" else None
        )

        self.fields: List[
            Union[
                GrammarElementFieldString,
                GrammarElementFieldMultipleChoice,
                GrammarElementFieldSingleChoice,
            ]
        ] = fields
        self.relations: List[
            Union[
                GrammarElementRelationParent,
                GrammarElementRelationChild,
                GrammarElementRelationFile,
            ]
        ] = relations if relations is not None and len(relations) > 0 else []
        fields_map: OrderedDict[str, GrammarElementField] = OrderedDict()

        statement_field: Optional[Tuple[str, int]] = None
        description_field: Optional[Tuple[str, int]] = None
        content_field: Optional[Tuple[str, int]] = None
        for field_idx_, field_ in enumerate(fields):
            fields_map[field_.title] = field_
            if field_.title == RequirementFieldName.STATEMENT:
                statement_field = (RequirementFieldName.STATEMENT, field_idx_)
            elif field_.title == "DESCRIPTION":
                description_field = (
                    RequirementFieldName.DESCRIPTION,
                    field_idx_,
                )
            elif field_.title == "CONTENT":
                content_field = (RequirementFieldName.CONTENT, field_idx_)
            else:
                pass
        self.fields_map: Dict[str, GrammarElementField] = fields_map

        self.field_titles: List[str] = list(
            map(lambda field__: field__.title, self.fields)
        )

        self.content_field: Tuple[str, int] = (
            statement_field or description_field or content_field or ("", -1)
        )

        # Use TITLE as a boundary between the single-line and multiline, if
        # TITLE exists. For nodes without a TITLE, use the content field, e.g.,
        # STATEMENT or DESCRIPTION.
        try:
            multiline_field_index = self.get_field_titles().index("TITLE") + 1
        except ValueError:
            multiline_field_index = self.content_field[1]
            if multiline_field_index == -1:
                raise StrictDocException(
                    (
                        f"The grammar element {self.tag} must have at least one of the "
                        f"following fields: TITLE, STATEMENT, DESCRIPTION, CONTENT."
                    ),
                ) from None
        self.multiline_field_index: int = multiline_field_index

        self.mid: MID = MID.create()
        self.ng_line_start: Optional[int] = None
        self.ng_col_start: Optional[int] = None

    @staticmethod
    def create_default(tag: str) -> "GrammarElement":
        return GrammarElement(
            parent=None,
            tag=tag,
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=[
                GrammarElementFieldString(
                    parent=None,
                    title="UID",
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title="TITLE",
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title="STATEMENT",
                    human_title=None,
                    required="False",
                ),
            ],
            relations=[],
        )

    @staticmethod
    def create_default_relations(
        parent: "GrammarElement",
    ) -> List[
        Union[
            GrammarElementRelationParent,
            GrammarElementRelationChild,
            GrammarElementRelationFile,
        ]
    ]:
        return [
            GrammarElementRelationParent(
                parent=parent,
                relation_type="Parent",
                relation_role=None,
            ),
            GrammarElementRelationFile(
                parent=parent,
                relation_type="File",
                relation_role=None,
            ),
        ]

    def is_field_multiline(self, field_name: str) -> bool:
        field_index = self.field_titles.index(field_name)
        try:
            title_field_index = self.field_titles.index("TITLE")
            if field_index <= title_field_index:
                return False
        except ValueError:
            pass
        return field_index >= self.content_field[1]

    def get_multiline_field_index(self) -> int:
        return self.multiline_field_index

    def get_view_style(self) -> Optional[str]:
        if self.property_view_style_lower is not None:
            return self.property_view_style_lower
        # For backward compatibility with older versions that didn't have the
        # [[NODE]] syntax and didn't enter the corresponding template migration,
        # keep the TEXT nodes to have a "plain" style unless their type is
        # specified by the grammar.
        if self.tag == "TEXT":
            return "plain"
        return None

    def get_relation_types(self) -> List[str]:
        return list(
            map(lambda relation_: relation_.relation_type, self.relations)
        )

    def get_field_titles(self) -> List[str]:
        return self.field_titles

    def get_tag_lower(self) -> str:
        return self.tag.lower()

    def has_relation_type_role(
        self, relation_type: str, relation_role: Optional[str]
    ) -> bool:
        assert relation_role is None or len(relation_role) > 0
        for relation_ in self.relations:
            if (
                relation_.relation_type == relation_type
                and relation_.relation_role == relation_role
            ):
                return True
        return False

    def enumerate_meta_field_titles(self) -> Generator[str, None, None]:
        for field in self.fields:
            if field.title in (
                RequirementFieldName.TITLE,
                RequirementFieldName.STATEMENT,
            ):
                break
            if field.title in RESERVED_NON_META_FIELDS:
                continue
            yield field.title

    def enumerate_custom_content_field_titles(
        self,
    ) -> Generator[str, None, None]:
        after_title_or_statement = False
        for field in self.fields:
            if field.title in (
                RequirementFieldName.TITLE,
                RequirementFieldName.STATEMENT,
            ):
                after_title_or_statement = True
            if field.title in RESERVED_NON_META_FIELDS:
                continue
            if not after_title_or_statement:
                continue
            yield field.title


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
