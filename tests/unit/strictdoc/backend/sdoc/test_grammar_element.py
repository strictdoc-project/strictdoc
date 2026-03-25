from strictdoc.backend.sdoc.models.document_grammar import (
    GrammarElement,
    GrammarElementFieldString,
)


def test_grammar_element_boundary_between_single_and_multiline_fields():
    fields = [
        GrammarElementFieldString(
            parent=None,
            title="MID",
            human_title=None,
            required="False",
        ),
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
            title="NAME",
            human_title=None,
            required="False",
        ),
        GrammarElementFieldString(
            parent=None,
            title="TYPE",
            human_title=None,
            required="False",
        ),
        GrammarElementFieldString(
            parent=None,
            title="CONTENT",
            human_title=None,
            required="False",
        ),
        GrammarElementFieldString(
            parent=None,
            title="NOTE",
            human_title=None,
            required="False",
        ),
    ]

    element = GrammarElement(
        parent=None,
        tag="DDITEM",
        property_is_composite="",
        property_prefix="",
        property_view_style="",
        fields=fields,
        relations=[],
    )

    assert element.is_field_multiline("MID") is False
    assert element.is_field_multiline("UID") is False
    assert element.is_field_multiline("TITLE") is False
    assert element.is_field_multiline("NAME") is False
    assert element.is_field_multiline("TYPE") is False
    assert element.is_field_multiline("CONTENT") is True
    assert element.is_field_multiline("NOTE") is True
