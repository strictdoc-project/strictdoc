from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
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

    requirement.set_field_value("STATEMENT", "Test statement")
    assert len(requirement.ordered_fields_lookup) == 1
    assert enumerate_field_titles(requirement) == ["STATEMENT"]

    requirement.set_field_value("TITLE", "Test title")
    assert len(requirement.ordered_fields_lookup) == 2
    assert enumerate_field_titles(requirement) == ["TITLE", "STATEMENT"]

    requirement.set_field_value("UID", "Test UID")
    assert len(requirement.ordered_fields_lookup) == 3
    assert enumerate_field_titles(requirement) == ["UID", "TITLE", "STATEMENT"]

    requirement.set_field_value("RATIONALE", "Test Rationale")
    assert len(requirement.ordered_fields_lookup) == 4
    assert enumerate_field_titles(requirement) == [
        "UID",
        "TITLE",
        "STATEMENT",
        "RATIONALE",
    ]
