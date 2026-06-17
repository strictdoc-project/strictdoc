import pytest

from strictdoc.backend.markdown.grammar_reader import MarkdownGrammarReader
from strictdoc.backend.markdown.reader import SDMarkdownReader
from strictdoc.backend.markdown.writer import (
    MarkdownGrammarWriter,
    SDMarkdownWriter,
)
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.node import SDocNode


def test_001_markdown_grammar_reader_parses_default_model():
    input_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Field: ASIL

**Type**: SingleChoice(A, B, C, D)
**Human Title**: Safety Level
**Required**: True

### Relations

#### Relation: Parent

#### Relation: File

**Role**: Implements
"""

    grammar = MarkdownGrammarReader.read(input_markdown)

    requirement = grammar.elements_by_type["REQUIREMENT"]
    assert requirement.fields_map["UID"].gef_type == "String"
    assert requirement.fields_map["ASIL"].required is True
    assert requirement.fields_map["ASIL"].human_title == "Safety Level"
    assert requirement.fields_map["ASIL"].options == ["A", "B", "C", "D"]
    assert requirement.relations[0].relation_type == "Parent"
    assert requirement.relations[1].relation_type == "File"
    assert requirement.relations[1].relation_role == "Implements"


def test_002_markdown_grammar_writer_roundtrips_default_markdown_grammar():
    input_markdown = """\
# StrictDoc Markdown Grammar

## Element: SECTION

**Composite**: True

### Field: TITLE

**Type**: String
**Required**: True

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Relations

#### Relation: Parent
"""

    grammar = MarkdownGrammarReader.read(input_markdown)
    output_markdown = MarkdownGrammarWriter.write(grammar)
    grammar_roundtrip = MarkdownGrammarReader.read(output_markdown)

    assert output_markdown == input_markdown
    assert (
        grammar_roundtrip.elements_by_type.keys()
        == grammar.elements_by_type.keys()
    )


def test_003_markdown_document_grammar_metadata_sets_import_from_file():
    input_markdown = """\
# Document example

**Grammar**: `requirements.gra.md`

## Requirement title

**UID**: REQ-1

**Statement**: System shall do X.
"""

    document = SDMarkdownReader.read(input_markdown, file_path=None)

    assert document.grammar is not None
    assert document.grammar.import_from_file == "requirements.gra.md"
    output_markdown = SDMarkdownWriter.write(document)
    assert "**Grammar**: requirements.gra.md" in output_markdown


def test_004_markdown_grammar_custom_grammar_relaxes_uid_and_statement_requirement():
    """
    When a document declares a Grammar import, _parse_markdown_node must accept
    heading nodes that lack UID/MID and STATEMENT, because those constraints
    belong to the default grammar only.  Field validation is deferred to the
    TraceabilityIndexBuilder.
    """
    input_markdown = """\
# Markdown document

**Grammar**: `requirements.gra.md`

## Component without UID

**ASIL**: B
**Name**: Widget
"""

    document = SDMarkdownReader.read(input_markdown, file_path=None)

    # The heading should be recognised as a REQUIREMENT node, not a plain section.
    assert len(document.section_contents) == 1
    node = document.section_contents[0]
    assert isinstance(node, SDocNode)
    assert node.node_type == "REQUIREMENT"
    assert node.reserved_title == "Component without UID"
    # Both custom fields must be present on the node.
    field_names = {f.field_name for f in node.enumerate_fields()}
    assert "ASIL" in field_names
    assert "NAME" in field_names


def test_005_markdown_grammar_writer_uses_field_key_not_human_title_for_custom_grammar():
    """
    Regression test for https://github.com/strictdoc-project/strictdoc/issues/2918.

    When a document has a custom (imported) grammar whose fields carry a
    Human Title, the writer must serialise each field using the grammar key
    name (e.g. DERIVED_RATIONALE), not the human-readable title
    (e.g. "Example Human Title").  The reader canonicalises field names with
    .upper(), so writing the human title produces an unrecoverable key on
    the next parse.
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Field: DERIVED_RATIONALE

**Type**: String
**Human Title**: Example Human Title
**Required**: False

### Relations

#### Relation: Parent
"""
    doc_markdown = """\
# Document

**Grammar**: `requirements.gra.md`

## Requirement title

**UID**: REQ-1
**DERIVED_RATIONALE**: Some rationale text.
"""

    document = SDMarkdownReader.read(doc_markdown, file_path=None)
    assert document.grammar is not None
    assert document.grammar.import_from_file == "requirements.gra.md"

    # Simulate grammar resolution (normally done by TraceabilityIndexBuilder).
    resolved_grammar = MarkdownGrammarReader.read(grammar_markdown)
    resolved_grammar.import_from_file = "requirements.gra.md"
    resolved_grammar.parent = document
    document.grammar = resolved_grammar

    output_markdown = SDMarkdownWriter.write(document)

    # The field key name must appear on disk, not the human title.
    assert "**DERIVED_RATIONALE**" in output_markdown
    assert "Example Human Title" not in output_markdown


def test_006_markdown_grammar_reader_rejects_unknown_field_type():
    input_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: Unknown
**Required**: False
"""

    with pytest.raises(StrictDocSemanticError) as exc_info:
        MarkdownGrammarReader.read(input_markdown)
    assert "unknown field Type" in exc_info.value.title
