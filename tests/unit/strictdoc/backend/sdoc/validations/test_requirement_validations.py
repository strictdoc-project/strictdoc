import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.validations.sdoc_validator import (
    SDocValidator,
    multi_choice_regex_match,
)
from strictdoc.core.document_iterator import DocumentCachingIterator


def test_01_positive():
    assert multi_choice_regex_match("A, B") is True


def test_02_positive():
    assert multi_choice_regex_match("TAG1, TAG2, TAG3") is True


def test_03_negative():
    assert multi_choice_regex_match("A,B") is False


def test_10_grammar_refs_file_only():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(FileReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
- TYPE: File
  VALUE: /tmp/sample1.cpp
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = DocumentCachingIterator(document)
    with pytest.raises(Exception) as exc_info:
        for node_ in document_iterator.all_content(
            print_fragments=False, print_fragments_from_files=False
        ):
            SDocValidator.validate_node(
                node_,
                document_grammar=document.grammar,
                path_to_sdoc_file="TEST.sdoc",
            )

    assert exc_info.type is StrictDocSemanticError
    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: Parent."
    )
    assert exception.hint == "Problematic requirement: ID-002."


def test_11_grammar_refs_validate_not_registered_file_relation():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
- TYPE: File
  VALUE: /tmp/sample1.cpp
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = DocumentCachingIterator(document)
    with pytest.raises(Exception) as exc_info:
        for node_ in document_iterator.all_content(
            print_fragments=False, print_fragments_from_files=False
        ):
            SDocValidator.validate_node(
                node_,
                document_grammar=document.grammar,
                path_to_sdoc_file="test.sdoc",
            )

    assert exc_info.type is StrictDocSemanticError
    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: File."
    )


def test_12_grammar_refs_validate_not_registered_parent_relation():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ChildReqReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = DocumentCachingIterator(document)
    with pytest.raises(Exception) as exc_info:
        for node_ in document_iterator.all_content(
            print_fragments=False, print_fragments_from_files=False
        ):
            SDocValidator.validate_node(
                node_,
                document_grammar=document.grammar,
                path_to_sdoc_file="test.sdoc",
            )

    assert exc_info.type is StrictDocSemanticError
    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: Parent."
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
REFS:
- TYPE: Child
  VALUE: ID-001
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = DocumentCachingIterator(document)
    with pytest.raises(Exception) as exc_info:
        for node_ in document_iterator.all_content(
            print_fragments=False, print_fragments_from_files=False
        ):
            SDocValidator.validate_node(
                node_,
                document_grammar=document.grammar,
                path_to_sdoc_file="test.sdoc",
            )

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
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()
    document = reader.read(input_sdoc)

    document_iterator = DocumentCachingIterator(document)
    with pytest.raises(Exception) as exc_info:
        for node_ in document_iterator.all_content(
            print_fragments=False, print_fragments_from_files=False
        ):
            SDocValidator.validate_node(
                node_,
                document_grammar=document.grammar,
                path_to_sdoc_file="test.sdoc",
            )

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: Parent / Refines."
    )
    assert exception.hint == "Problematic requirement: REQ-001."
