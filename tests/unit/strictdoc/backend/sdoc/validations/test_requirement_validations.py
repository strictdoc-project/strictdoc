from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.type_system import GrammarElementFieldString
from strictdoc.backend.sdoc.validations.requirement import (
    multi_choice_regex_match,
)


def test_01_positive():
    assert multi_choice_regex_match("A, B") is True


def test_02_positive():
    assert multi_choice_regex_match("TAG1, TAG2, TAG3") is True


def test_03_negative():
    assert multi_choice_regex_match("A,B") is False


# FIXME: This test does not belong here.
def test_04_meta_multilines_not_nones():
    document_config = DocumentConfig.default_config(None)
    document = Document("Test Doc", document_config, None, [], [])

    test_field = "META_TEST_FIELD"
    fields = DocumentGrammar.create_default(document).elements[0].fields

    fields.extend(
        [
            GrammarElementFieldString(
                parent=None, title=test_field, required="False"
            ),
        ]
    )

    requirements_element = GrammarElement(
        parent=None, tag="REQUIREMENT", fields=fields
    )
    elements = [requirements_element]
    grammar = DocumentGrammar(parent=document, elements=elements)
    document.grammar = grammar

    template_requirement = SDocObjectFactory.create_requirement(
        document,
        requirement_type="REQUIREMENT",
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
    fields = list(template_requirement.enumerate_fields())
    fields.append(
        RequirementField(
            parent=None,
            field_name=test_field,
            field_value=None,
            field_value_multiline=(
                "a long\nmultiline value instead\nof the single line one"
            ),
            field_value_references=None,
        )
    )
    requirement = Requirement(
        parent=template_requirement.parent,
        requirement_type=template_requirement.requirement_type,
        fields=fields,
    )
    requirement.ng_level = 1

    for name, value in requirement.enumerate_meta_fields():
        assert value is not None
