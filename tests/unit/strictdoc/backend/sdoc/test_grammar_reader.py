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


def test_faulty_grammar():
    input_sdoc = """
[GRAMMAR MISTAKE]
""".lstrip()

    reader = SDocGrammarReader()

    with pytest.raises(StrictDocException) as exc_info_:
        _ = reader.read(input_sdoc)

    assert isinstance(exc_info_.value, Exception)
