import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.validations.sdoc_validator import (
    SDocValidator,
    multi_choice_regex_match,
)
from strictdoc.core.document_iterator import SDocDocumentIterator
from tests.unit.helpers.fake_document_meta import create_fake_document_meta


def test_01_positive():
    assert multi_choice_regex_match("A, B") is True


def test_02_positive():
    assert multi_choice_regex_match("TAG1, TAG2, TAG3") is True


def test_03_negative():
    assert multi_choice_regex_match("A,B") is False


def test_10_single_choice_tbd_accepted():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: CHOICE_FIELD
    TYPE: SingleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
CHOICE_FIELD: TBD
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = SDocDocumentIterator(document)
    for node_, _ in document_iterator.all_content(print_fragments=False):
        SDocValidator.validate_node(
            node_,
            document_grammar=document.grammar,
            path_to_sdoc_file="test.sdoc",
        )


def test_11_single_choice_tbc_accepted():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: CHOICE_FIELD
    TYPE: SingleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
CHOICE_FIELD: TBC
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = SDocDocumentIterator(document)
    for node_, _ in document_iterator.all_content(print_fragments=False):
        SDocValidator.validate_node(
            node_,
            document_grammar=document.grammar,
            path_to_sdoc_file="test.sdoc",
        )


def test_12_multiple_choice_tbd_accepted():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
CHOICE_FIELD: TBD
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = SDocDocumentIterator(document)
    for node_, _ in document_iterator.all_content(print_fragments=False):
        SDocValidator.validate_node(
            node_,
            document_grammar=document.grammar,
            path_to_sdoc_file="test.sdoc",
        )


def test_13_multiple_choice_tbc_accepted():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
CHOICE_FIELD: TBC
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = SDocDocumentIterator(document)
    for node_, _ in document_iterator.all_content(print_fragments=False):
        SDocValidator.validate_node(
            node_,
            document_grammar=document.grammar,
            path_to_sdoc_file="test.sdoc",
        )


def test_14_multiple_choice_mixed_with_tbd_accepted():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
CHOICE_FIELD: A, TBD
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = SDocDocumentIterator(document)
    for node_, _ in document_iterator.all_content(print_fragments=False):
        SDocValidator.validate_node(
            node_,
            document_grammar=document.grammar,
            path_to_sdoc_file="test.sdoc",
        )


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


def test_22_validate_reverse_role_requires_role():
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
    REVERSE_ROLE: Refined by

[REQUIREMENT]
UID: REQ-001
STATEMENT: This is a statement.
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)
    document.meta = create_fake_document_meta()

    with pytest.raises(StrictDocSemanticError) as exc_info:
        SDocValidator.validate_document(document)

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Grammar element 'REQUIREMENT' defines REVERSE_ROLE without ROLE "
        "for relation type 'Parent'."
    )


def test_23_validate_text_element_must_not_be_composite():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  PROPERTIES:
    IS_COMPOSITE: True
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
UID: REQ-001
STATEMENT: This is a statement.
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)
    document.meta = create_fake_document_meta()

    with pytest.raises(StrictDocSemanticError) as exc_info:
        SDocValidator.validate_document(document)

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "The TEXT grammar element must not be declared as composite."
    )


def test_24_validate_section_element_must_be_composite():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: SECTION
  PROPERTIES:
    IS_COMPOSITE: False
  FIELDS:
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
UID: REQ-001
STATEMENT: This is a statement.
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)
    document.meta = create_fake_document_meta()

    with pytest.raises(StrictDocSemanticError) as exc_info:
        SDocValidator.validate_document(document)

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "The SECTION grammar element must be declared as composite."
    )
