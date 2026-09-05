"""
Coverage for SDWriter.write_grammar_file_content()/write_grammar_elements(),
the serializer a standalone .sgra file (an IMPORT_FROM_FILE target) needs —
added so the grammar editor can write an edited grammar back to that file
instead of silently discarding the change. See
strictdoc/core/grammar_file_resolver.py and
strictdoc/server/routers/main_router.py::write_grammar_change_to_file.
"""

from strictdoc.backend.sdoc.grammar_reader import SDocGrammarReader
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    RequirementFieldType,
)
from strictdoc.backend.sdoc.writer import SDWriter

INPUT_SGRA = """\
[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  - TITLE: TARGET_REVISION
    TYPE: SingleChoice(C1, C2)
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent
    ROLE: COVERS
"""


def test_write_grammar_file_content_matches_the_shape_of_a_real_sgra_file():
    document_grammar = SDocGrammarReader().read(INPUT_SGRA)

    output = SDWriter.write_grammar_file_content(document_grammar)

    assert output == INPUT_SGRA


def test_written_grammar_file_content_re_parses_to_the_same_elements():
    document_grammar = SDocGrammarReader().read(INPUT_SGRA)

    output = SDWriter.write_grammar_file_content(document_grammar)
    reparsed_grammar = SDocGrammarReader().read(output)

    assert isinstance(reparsed_grammar, DocumentGrammar)
    element = reparsed_grammar.elements_by_type["REQUIREMENT"]
    target_revision_field = element.fields_map["TARGET_REVISION"]
    assert isinstance(target_revision_field, GrammarElementFieldSingleChoice)
    assert target_revision_field.options == ["C1", "C2"]


def test_write_grammar_elements_reflects_an_in_memory_edit():
    # Simulates what the grammar editor does: mutate the in-memory
    # DocumentGrammar (here, append a new TARGET_REVISION option), then
    # serialize it — this is the exact step
    # write_grammar_change_to_file() performs before writing to disk.
    document_grammar = SDocGrammarReader().read(INPUT_SGRA)
    element = document_grammar.elements_by_type["REQUIREMENT"]
    target_revision_field = element.fields_map["TARGET_REVISION"]
    assert isinstance(target_revision_field, GrammarElementFieldSingleChoice)
    target_revision_field.options.append("D1")

    output = SDWriter.write_grammar_elements(document_grammar)

    assert "TYPE: SingleChoice(C1, C2, D1)" in output


def test_a_string_field_produces_no_options():
    field = GrammarElementFieldString(
        parent=None, title="NOTE", human_title=None, required="False"
    )
    assert field.gef_type == RequirementFieldType.STRING

    output = SDWriter._print_grammar_field_type(field)

    assert output == "  - TITLE: NOTE\n    TYPE: String\n    REQUIRED: False\n"
