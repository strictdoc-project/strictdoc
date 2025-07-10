from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElementFieldString,
)
from strictdoc.backend.sdoc.models.node import SDocNodeField
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory


def test_01_empty_requirement_as_starting_point():
    document = SDocObjectFactory.create_document("TestDoc")
    document.grammar = DocumentGrammar.create_default(document)

    requirement = SDocObjectFactory.create_requirement(
        parent=document,
    )
    assert len(requirement.ordered_fields_lookup) == 0


def test_02_mutating_with_a_field():
    def enumerate_field_titles(requirement):
        return list(map(lambda f: f.field_name, requirement.enumerate_fields()))

    document = SDocObjectFactory.create_document("TestDoc")
    document.grammar = DocumentGrammar.create_default(document)

    requirement = SDocObjectFactory.create_requirement(
        parent=document,
    )

    requirement.set_field_value(
        field_name="STATEMENT", form_field_index=0, value="Test statement"
    )
    assert len(requirement.ordered_fields_lookup) == 1
    assert enumerate_field_titles(requirement) == ["STATEMENT"]

    requirement.set_field_value(
        field_name="TITLE", form_field_index=0, value="Test title"
    )
    assert len(requirement.ordered_fields_lookup) == 2
    assert enumerate_field_titles(requirement) == ["TITLE", "STATEMENT"]

    requirement.set_field_value(
        field_name="UID", form_field_index=0, value="Test UID"
    )
    assert len(requirement.ordered_fields_lookup) == 3
    assert enumerate_field_titles(requirement) == ["UID", "TITLE", "STATEMENT"]

    requirement.set_field_value(
        field_name="RATIONALE", form_field_index=0, value="Test Rationale"
    )
    assert len(requirement.ordered_fields_lookup) == 4
    assert enumerate_field_titles(requirement) == [
        "UID",
        "TITLE",
        "STATEMENT",
        "RATIONALE",
    ]


def test_04_meta_multilines_not_nones():
    document_config = DocumentConfig.default_config(None)
    document = SDocDocument(
        mid=None,
        title="Test Doc",
        config=document_config,
        view=None,
        grammar=None,
        section_contents=[],
    )
    grammar: DocumentGrammar = DocumentGrammar.create_default(document)

    meta_test_field = GrammarElementFieldString(
        parent=None,
        title="META_TEST_FIELD",
        human_title=None,
        required="False",
    )
    requirement_grammar_element = grammar.elements_by_type["REQUIREMENT"]
    requirement_grammar_element.fields.append(meta_test_field)
    requirement_grammar_element.fields_map["META_TEST_FIELD"] = meta_test_field
    document.grammar = grammar

    requirement = SDocObjectFactory.create_requirement(
        document,
        node_type="REQUIREMENT",
        title=None,
        uid="A-1",
        level=None,
        statement=None,
        statement_multiline="the bar must foo",
        rationale=None,
        rationale_multiline=None,
        tags=None,
        comments=None,
    )

    test_value = "a long\nmultiline value instead\nof the single line one"
    requirement.ordered_fields_lookup["META_TEST_FIELD"] = [
        SDocNodeField.create_from_string(
            parent=None,
            field_name="META_TEST_FIELD",
            field_value=test_value,
            multiline=True,
        )
    ]
    meta_fields = list(requirement.enumerate_meta_fields())
    assert meta_fields[0][1].get_text_value() == "A-1"
    assert meta_fields[1][1].get_text_value() == test_value

    singleline_meta_fields = list(
        requirement.enumerate_meta_fields(skip_multi_lines=True)
    )
    assert len(singleline_meta_fields) == 1
    assert singleline_meta_fields[0][1].get_text_value() == "A-1"

    multiline_meta_fields = list(
        requirement.enumerate_meta_fields(skip_single_lines=True)
    )
    assert len(multiline_meta_fields) == 1
    assert multiline_meta_fields[0][1].get_text_value() == test_value
