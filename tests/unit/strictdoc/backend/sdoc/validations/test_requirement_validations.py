import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.validations.sdoc_validator import (
    SDocValidator,
    multi_choice_regex_match,
)
from strictdoc.core.document_iterator import SDocDocumentIterator


def test_01_positive():
    assert multi_choice_regex_match("A, B") is True


def test_02_positive():
    assert multi_choice_regex_match("TAG1, TAG2, TAG3") is True


def test_03_negative():
    assert multi_choice_regex_match("A,B") is False


def test_21_validate_unregistered_child_relation_type():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent

[REQUIREMENT]
UID: ID-002
STATEMENT: >>>
This is a statement.
<<<
RELATIONS:
- TYPE: Child
  VALUE: ID-001
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = SDocDocumentIterator(document)
    with pytest.raises(StrictDocSemanticError) as exc_info:
        for node_, _ in document_iterator.all_content(print_fragments=False):
            SDocValidator.validate_node(
                node_,
                document_grammar=document.grammar,
                path_to_sdoc_file="test.sdoc",
            )
        raise AssertionError

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: Child."
    )
    assert exception.hint == "Problematic requirement: ID-002."


def test_21_validate_unregistered_role():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
UID: REQ-001
STATEMENT: >>>
This is a statement.
<<<
RELATIONS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = SDocDocumentIterator(document)
    with pytest.raises(StrictDocSemanticError) as exc_info:
        for node_, _ in document_iterator.all_content(print_fragments=False):
            SDocValidator.validate_node(
                node_,
                document_grammar=document.grammar,
                path_to_sdoc_file="test.sdoc",
            )
        raise AssertionError

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: Parent / Refines."
    )
    assert exception.hint == "Problematic requirement: REQ-001."
