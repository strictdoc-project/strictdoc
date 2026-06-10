import pytest

from strictdoc.backend.sdoc.grammar_reader import SDocGrammarReader
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.helpers.exception import StrictDocException


def test_health_grammar():
    input_sdoc = """
[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  FIELDS:
  - TITLE: MID
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
""".lstrip()

    reader = SDocGrammarReader()

    grammar = reader.read(input_sdoc)
    assert isinstance(grammar, DocumentGrammar)


def test_grammar_from_file_supports_reverse_role():
    input_sdoc = """
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
    ROLE: Refines
    REVERSE_ROLE: Refined by
  - TYPE: Child
    ROLE: Verifies
    REVERSE_ROLE: Verified by
""".lstrip()

    reader = SDocGrammarReader()

    grammar = reader.read(input_sdoc)
    assert isinstance(grammar, DocumentGrammar)
    requirement = grammar.elements_by_type["REQUIREMENT"]

    parent_relation = requirement.relations[0]
    assert parent_relation.relation_type == "Parent"
    assert parent_relation.relation_role == "Refines"
    assert parent_relation.reverse_relation_role == "Refined by"

    child_relation = requirement.relations[1]
    assert child_relation.relation_type == "Child"
    assert child_relation.relation_role == "Verifies"
    assert child_relation.reverse_relation_role == "Verified by"


def test_faulty_grammar():
    input_sdoc = """
[GRAMMAR MISTAKE]
""".lstrip()

    reader = SDocGrammarReader()

    with pytest.raises(StrictDocException) as exc_info_:
        _ = reader.read(input_sdoc)

    assert isinstance(exc_info_.value, Exception)
