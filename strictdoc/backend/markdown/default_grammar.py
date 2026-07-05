from typing import List, Optional

from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementFieldString,
    GrammarElementFieldType,
)
from strictdoc.backend.sdoc.models.model import SDocDocumentIF


def create_markdown_default_grammar(
    parent: Optional[SDocDocumentIF],
    enable_mid: bool = False,
    include_child_relation: bool = False,
) -> DocumentGrammar:
    """
    Build the Markdown-only default grammar.

    This mirrors DocumentGrammar.create_default() (shared with SDoc) field
    for field, but sets a Title-Case human_title on every field beyond MID/UID
    (kept as uppercase abbreviations). The field *title* (the internal key
    used by SDocNode.ordered_fields_lookup and GrammarElement's content-field
    detection) is left as the shared ALL_CAPS constant so that node.rationale,
    node.reserved_title, node.reserved_level, etc. keep working unmodified.
    SDMarkdownReader/SDMarkdownWriter alias the Title-Case surface syntax
    (**Statement**:, **Rationale**:, ...) onto these keys at the text level.
    """
    text_element = _create_text_element(enable_mid=enable_mid)
    section_element = _create_section_element(enable_mid=enable_mid)

    fields: List[GrammarElementFieldType] = []
    if enable_mid:
        fields.append(
            GrammarElementFieldString(
                parent=None, title="MID", human_title=None, required="False"
            )
        )
    fields.extend(
        [
            GrammarElementFieldString(
                parent=None, title="UID", human_title=None, required="False"
            ),
            GrammarElementFieldString(
                parent=None,
                title="LEVEL",
                human_title="Level",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATUS",
                human_title="Status",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TAGS",
                human_title="Tags",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title="Title",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title="Statement",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="RATIONALE",
                human_title="Rationale",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="COMMENT",
                human_title="Comment",
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
    requirement_element.relations = GrammarElement.create_default_relations(
        requirement_element,
        include_child=include_child_relation,
    )

    elements: List[GrammarElement] = [
        section_element,
        text_element,
        requirement_element,
    ]

    grammar = DocumentGrammar(
        parent=parent, elements=elements, import_from_file=None
    )
    grammar.is_default = True
    text_element.parent = grammar
    section_element.parent = grammar
    requirement_element.parent = grammar

    return grammar


def _create_text_element(enable_mid: bool = False) -> GrammarElement:
    fields: List[GrammarElementFieldType] = []
    if enable_mid:
        fields.append(
            GrammarElementFieldString(
                parent=None, title="MID", human_title=None, required="False"
            )
        )
    fields.extend(
        [
            GrammarElementFieldString(
                parent=None, title="UID", human_title=None, required="False"
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title="Statement",
                required="True",
            ),
        ]
    )
    return GrammarElement(
        parent=None,
        tag="TEXT",
        property_is_composite="",
        property_prefix="",
        property_view_style="",
        fields=fields,
        relations=[],
    )


def _create_section_element(enable_mid: bool = False) -> GrammarElement:
    fields: List[GrammarElementFieldType] = []
    if enable_mid:
        fields.append(
            GrammarElementFieldString(
                parent=None, title="MID", human_title=None, required="False"
            )
        )
    fields.extend(
        [
            GrammarElementFieldString(
                parent=None, title="UID", human_title=None, required="False"
            ),
            GrammarElementFieldString(
                parent=None,
                title="LEVEL",
                human_title="Level",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="PREFIX",
                human_title="Prefix",
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title="Title",
                required="True",
            ),
        ]
    )
    return GrammarElement(
        parent=None,
        tag="SECTION",
        property_is_composite="True",
        property_prefix="",
        property_view_style="",
        fields=fields,
        relations=[],
    )
