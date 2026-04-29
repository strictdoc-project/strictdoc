from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
    GrammarElementFieldString,
)


def _make_field(title):
    return GrammarElementFieldString(
        parent=None,
        title=title,
        human_title=None,
        required="False",
    )


def _make_element(tag, field_titles):
    return GrammarElement(
        parent=None,
        tag=tag,
        property_is_composite="",
        property_prefix="",
        property_view_style="",
        fields=[_make_field(title_) for title_ in field_titles],
        relations=[],
    )


def _make_document_with_elements(elements):
    document = SDocDocument(
        mid=None,
        title="Test",
        config=None,
        view=None,
        grammar=None,
        section_contents=[],
    )
    grammar = DocumentGrammar(
        parent=document,
        elements=elements,
    )
    document.grammar = grammar
    return document


def test_enumerate_meta_field_titles_single_element():
    element = _make_element(
        "REQUIREMENT",
        ["UID", "SEVERITY", "TITLE", "STATEMENT"],
    )
    document = _make_document_with_elements([element])

    result = list(document.enumerate_meta_field_titles())

    assert result == ["UID", "SEVERITY"]


def test_enumerate_meta_field_titles_multiple_elements_no_duplicates():
    element_a = _make_element(
        "REQUIREMENT",
        ["UID", "SEVERITY", "TITLE", "STATEMENT"],
    )
    element_b = _make_element(
        "CUSTOM",
        ["UID", "PRIORITY", "TITLE", "STATEMENT"],
    )
    document = _make_document_with_elements([element_a, element_b])

    result = list(document.enumerate_meta_field_titles())

    assert result == ["UID", "SEVERITY", "PRIORITY"]


def test_enumerate_meta_field_titles_multiple_elements_with_common_fields():
    element_a = _make_element(
        "REQUIREMENT",
        ["UID", "SEVERITY", "TITLE", "STATEMENT"],
    )
    element_b = _make_element(
        "CUSTOM",
        ["UID", "SEVERITY", "PRIORITY", "TITLE", "STATEMENT"],
    )
    document = _make_document_with_elements([element_a, element_b])

    result = list(document.enumerate_meta_field_titles())

    assert result == ["UID", "SEVERITY", "PRIORITY"]


def test_enumerate_custom_content_field_titles_single_element():
    element = _make_element(
        "REQUIREMENT",
        ["UID", "TITLE", "STATEMENT", "NOTE"],
    )
    document = _make_document_with_elements([element])

    result = list(document.enumerate_custom_content_field_titles())

    assert result == ["NOTE"]


def test_enumerate_custom_content_field_titles_multiple_elements_no_duplicates():
    element_a = _make_element(
        "REQUIREMENT",
        ["UID", "TITLE", "STATEMENT", "NOTE"],
    )
    element_b = _make_element(
        "CUSTOM",
        ["UID", "TITLE", "STATEMENT", "IMPACT"],
    )
    document = _make_document_with_elements([element_a, element_b])

    result = list(document.enumerate_custom_content_field_titles())

    assert result == ["NOTE", "IMPACT"]


def test_enumerate_custom_content_field_titles_multiple_elements_with_common_fields():
    element_a = _make_element(
        "REQUIREMENT",
        ["UID", "TITLE", "STATEMENT", "NOTE"],
    )
    element_b = _make_element(
        "CUSTOM",
        ["UID", "TITLE", "STATEMENT", "NOTE", "IMPACT"],
    )
    document = _make_document_with_elements([element_a, element_b])

    result = list(document.enumerate_custom_content_field_titles())

    assert result == ["NOTE", "IMPACT"]
