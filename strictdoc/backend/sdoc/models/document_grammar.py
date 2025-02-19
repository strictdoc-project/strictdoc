# mypy: disable-error-code="no-untyped-call,no-untyped-def,union-attr,type-arg"
from collections import OrderedDict
from typing import Dict, Generator, List, Optional, Set, Tuple, Union

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
from strictdoc.helpers.mid import MID


def create_default_relations(
    parent,
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


@auto_described()
class GrammarElement:
    def __init__(
        self,
        parent,
        tag: str,
        fields: List[
            Union[
                GrammarElementFieldString,
                GrammarElementFieldMultipleChoice,
                GrammarElementFieldSingleChoice,
            ]
        ],
        relations: List,
    ):
        self.parent = parent
        self.tag: str = tag
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
        fields_map: OrderedDict = OrderedDict()

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
        self.content_field: Tuple[str, int] = (
            statement_field or description_field or content_field or ("", -1)
        )
        self.mid: MID = MID.create()
        self.ng_line_start: Optional[int] = None
        self.ng_col_start: Optional[int] = None

    @staticmethod
    def create_default(tag: str):
        return GrammarElement(
            parent=None,
            tag=tag,
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

    def get_multiline_field_index(self) -> int:
        multiline_field_index = self.content_field[1]
        assert multiline_field_index != -1
        return multiline_field_index

    def get_relation_types(self) -> List[str]:
        return list(
            map(lambda relation_: relation_.relation_type, self.relations)
        )

    def get_field_titles(self) -> List[str]:
        return list(map(lambda field_: field_.title, self.fields))

    def get_tag_lower(self) -> str:
        return self.tag.lower()

    def has_relation_type_role(
        self, relation_type: str, relation_role: Optional[str]
    ):
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


class DocumentGrammar:
    def __init__(
        self,
        parent,
        elements: List[GrammarElement],
        import_from_file: Optional[str] = None,
    ) -> None:
        self.parent = parent
        self.elements: List[GrammarElement] = elements

        self.registered_elements: Set[str] = set()
        self.elements_by_type: Dict[str, GrammarElement] = {}

        self.update_with_elements(elements)

        # textX passes an empty string instead of None when import_from_file is
        # not provided in input.
        if import_from_file is not None and len(import_from_file) == 0:
            import_from_file = None
        self.import_from_file: Optional[str] = import_from_file

        self.is_default = False

        self.ng_line_start: Optional[int] = None
        self.ng_col_start: Optional[int] = None

    @staticmethod
    def create_default(parent) -> "DocumentGrammar":
        text_element: GrammarElement = (
            DocumentGrammar.create_default_text_element()
        )

        # @relation(SDOC-SRS-132, scope=range_start)
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
        requirement_element = GrammarElement(
            parent=None, tag="REQUIREMENT", fields=fields, relations=[]
        )
        # @relation(SDOC-SRS-132, scope=range_end)

        requirement_element.relations = create_default_relations(
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

    @staticmethod
    def create_for_test_report(parent) -> "DocumentGrammar":
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
        ]
        requirement_element = GrammarElement(
            parent=None, tag="TEST_RESULT", fields=fields, relations=[]
        )

        requirement_element.relations = create_default_relations(
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

    def get_element_by_mid(self, element_mid: str):
        for element_ in self.elements:
            if element_.mid == element_mid:
                return element_
        raise AssertionError(
            f"Could not find a grammar element with MID: {element_mid}"
        )

    def dump_fields(self, node_type) -> str:
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

    def add_element_first(self, element: GrammarElement):
        self.elements.insert(0, element)
        self.elements_by_type[element.tag] = element
        self.registered_elements.add(element.tag)
        self.is_default = False

    def update_element(
        self, existing_element: GrammarElement, updated_element: GrammarElement
    ):
        element_index = self.elements.index(existing_element)
        self.elements[element_index] = updated_element
        self.elements_by_type[updated_element.tag] = updated_element
        self.is_default = False

    def update_with_elements(self, elements: List[GrammarElement]):
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
    def create_default_text_element(parent=None) -> GrammarElement:
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
                title=RequirementFieldName.STATEMENT,
                human_title=None,
                required="True",
            ),
        ]
        text_element = GrammarElement(
            parent=parent, tag="TEXT", fields=fields, relations=[]
        )
        return text_element


class DocumentGrammarWrapper:
    def __init__(self, grammar: DocumentGrammar):
        assert isinstance(grammar, DocumentGrammar), grammar
        self.grammar: DocumentGrammar = grammar
