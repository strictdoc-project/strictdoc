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
**Human title**: Safety Level
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


def test_002b_markdown_grammar_writer_roundtrips_composite_true_and_false():
    input_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

**Composite**: True

### Field: UID

**Type**: String
**Required**: False

## Element: TEXT

**Composite**: False

### Field: STATEMENT

**Type**: String
**Required**: False
"""

    grammar = MarkdownGrammarReader.read(input_markdown)

    requirement_element = grammar.elements_by_type["REQUIREMENT"]
    text_element = grammar.elements_by_type["TEXT"]
    assert requirement_element.property_is_composite is True
    assert text_element.property_is_composite is False

    output_markdown = MarkdownGrammarWriter.write(grammar)
    assert output_markdown == input_markdown

    grammar_roundtrip = MarkdownGrammarReader.read(output_markdown)
    requirement_element_roundtrip = grammar_roundtrip.elements_by_type[
        "REQUIREMENT"
    ]
    text_element_roundtrip = grammar_roundtrip.elements_by_type["TEXT"]
    assert requirement_element_roundtrip.property_is_composite is True
    assert text_element_roundtrip.property_is_composite is False


def test_003_markdown_document_grammar_metadata_sets_import_from_file():
    input_markdown = """\
# Document example

**Grammar**: `requirements.gra.md`

## Requirement title

**UID**: REQ-1

**STATEMENT**: System shall do X.
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
    assert "Name" in field_names


def test_005_markdown_grammar_writer_uses_field_key_not_human_title_for_custom_grammar():
    """
    Regression test for https://github.com/strictdoc-project/strictdoc/issues/2918.

    When a document has a custom (imported) grammar whose fields carry a
    Human title, the writer must serialise each field using the grammar key
    name (e.g. DERIVED_RATIONALE), not the human-readable title
    (e.g. "Example Human Title").  The reader matches field names exactly, so
    writing the human title would produce an unrecognized key on the next
    parse.
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Field: DERIVED_RATIONALE

**Type**: String
**Human title**: Example Human Title
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


def test_007_markdown_writer_auto_writes_mid_when_grammar_has_mid_field():
    """
    When a document's grammar declares a MID field and a node doesn't have
    MID set in the file, the Markdown writer must auto-write the
    reserved_mid value so that the MID becomes permanent on the next read.
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: MID

**Type**: String
**Required**: False

### Field: UID

**Type**: String
**Required**: False

### Field: STATEMENT

**Type**: String
**Required**: False
"""
    doc_markdown = """\
# Document

**Grammar**: `requirements.gra.md`

## Requirement title

**UID**: REQ-1

**STATEMENT**: System shall do X.
"""

    document = SDMarkdownReader.read(doc_markdown, file_path=None)
    assert document.grammar is not None

    # Simulate grammar resolution (normally done by TraceabilityIndexBuilder).
    resolved_grammar = MarkdownGrammarReader.read(grammar_markdown)
    resolved_grammar.import_from_file = "requirements.gra.md"
    resolved_grammar.parent = document
    document.grammar = resolved_grammar

    output_markdown = SDMarkdownWriter.write(document)

    # The writer must have inserted a MID field.
    assert "**MID**:" in output_markdown
    # UID must still be present.
    assert "**UID**: REQ-1" in output_markdown


def test_008_markdown_writer_preserves_existing_mid_when_grammar_has_mid_field():
    """
    When a document's grammar declares MID and a node already has a MID
    value in the document, the writer must preserve the existing MID value
    (no duplicate MID field).
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: MID

**Type**: String
**Required**: False

### Field: UID

**Type**: String
**Required**: False

### Field: STATEMENT

**Type**: String
**Required**: False
"""
    doc_markdown = """\
# Document

**Grammar**: `requirements.gra.md`

## Requirement title

**MID**: abc123 \\
**UID**: REQ-1

**STATEMENT**: System shall do X.
"""

    document = SDMarkdownReader.read(doc_markdown, file_path=None)
    assert document.grammar is not None

    # Simulate grammar resolution.
    resolved_grammar = MarkdownGrammarReader.read(grammar_markdown)
    resolved_grammar.import_from_file = "requirements.gra.md"
    resolved_grammar.parent = document
    document.grammar = resolved_grammar

    output_markdown = SDMarkdownWriter.write(document)

    # The existing MID must be preserved.
    assert "**MID**: abc123" in output_markdown
    # No duplicate MID field: count occurrences.
    assert output_markdown.count("**MID**") == 1
    assert "**UID**: REQ-1" in output_markdown


def test_009_markdown_writer_no_mid_when_grammar_has_no_mid_field():
    """
    When the grammar does not declare a MID field, the writer must not
    inject any MID field into the output even though nodes carry a
    reserved_mid internally.
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Field: STATEMENT

**Type**: String
**Required**: False
"""
    doc_markdown = """\
# Document

**Grammar**: `requirements.gra.md`

## Requirement title

**UID**: REQ-1

**STATEMENT**: System shall do X.
"""

    document = SDMarkdownReader.read(doc_markdown, file_path=None)

    # Simulate grammar resolution.
    resolved_grammar = MarkdownGrammarReader.read(grammar_markdown)
    resolved_grammar.import_from_file = "requirements.gra.md"
    resolved_grammar.parent = document
    document.grammar = resolved_grammar

    output_markdown = SDMarkdownWriter.write(document)

    assert "**MID**" not in output_markdown
    assert "**UID**: REQ-1" in output_markdown


def test_010_markdown_writer_injects_mid_into_section_nodes_when_grammar_declares_mid():
    """
    When a grammar declares a MID field for the SECTION element, the writer
    auto-injects MID into SECTION nodes that do not already carry one, and
    also emits Type: SECTION as the first meta field so the reader does not
    misidentify the heading as a REQUIREMENT on the next parse.
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: SECTION

**Composite**: True

### Field: MID

**Type**: String
**Required**: False

### Field: TITLE

**Type**: String
**Required**: True

## Element: REQUIREMENT

### Field: MID

**Type**: String
**Required**: False

### Field: UID

**Type**: String
**Required**: False

### Field: STATEMENT

**Type**: String
**Required**: False
"""
    doc_markdown = """\
# Document

**Grammar**: `requirements.gra.md`

## Section heading

### Requirement inside section

**UID**: REQ-1

**STATEMENT**: System shall do X.
"""

    document = SDMarkdownReader.read(doc_markdown, file_path=None)
    assert document.grammar is not None

    # Simulate grammar resolution (normally done by TraceabilityIndexBuilder).
    resolved_grammar = MarkdownGrammarReader.read(grammar_markdown)
    resolved_grammar.import_from_file = "requirements.gra.md"
    resolved_grammar.parent = document
    document.grammar = resolved_grammar

    output_markdown = SDMarkdownWriter.write(document)

    lines = output_markdown.splitlines()

    # The SECTION node must receive Type and MID injection.
    section_idx = next(
        i for i, line in enumerate(lines) if "Section heading" in line
    )
    section_block_lines = []
    for line in lines[section_idx + 1 :]:
        if line.startswith("#"):
            break
        section_block_lines.append(line)
    section_block = "\n".join(section_block_lines)
    assert "**Type**: SECTION" in section_block, (
        f"Type: SECTION not found in section block: {section_block!r}"
    )
    assert "**MID**:" in section_block, (
        f"MID not injected into section block: {section_block!r}"
    )

    # The REQUIREMENT node must also receive Type and MID injection.
    req_idx = next(
        i
        for i, line in enumerate(lines)
        if "Requirement inside section" in line
    )
    req_block_lines = []
    for line in lines[req_idx + 1 :]:
        if line.startswith("#"):
            break
        req_block_lines.append(line)
    req_block = "\n".join(req_block_lines)
    assert "**MID**:" in req_block, (
        f"MID not injected into requirement block: {req_block!r}"
    )


def test_011_markdown_grammar_reader_and_writer_roundtrip_reverse_role():
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Relations

#### Relation: Parent

**Role**: Refines
**Reverse role**: Refined by
"""

    grammar = MarkdownGrammarReader.read(grammar_markdown)
    relation = grammar.elements_by_type["REQUIREMENT"].relations[0]
    assert relation.relation_role == "Refines"
    assert relation.reverse_relation_role == "Refined by"

    output_markdown = MarkdownGrammarWriter.write(grammar)
    assert "**Role**: Refines" in output_markdown
    assert "**Reverse role**: Refined by" in output_markdown

    roundtrip_grammar = MarkdownGrammarReader.read(output_markdown)
    roundtrip_relation = roundtrip_grammar.elements_by_type[
        "REQUIREMENT"
    ].relations[0]
    assert roundtrip_relation.relation_role == "Refines"
    assert roundtrip_relation.reverse_relation_role == "Refined by"


def test_012_markdown_grammar_field_declared_in_camel_case():
    """
    A custom grammar is free to declare an arbitrary (non-reserved) field
    name in ALL_CAPS, Camel-Case, or Camel Case. SDMarkdownReader no longer
    normalizes parsed field names, so a document must write such a field
    using the exact casing declared by the grammar for it to be recognised;
    that casing is also what the writer reproduces on write-back.
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Field: Name

**Type**: String
**Required**: False
"""
    doc_markdown = """\
# Document

**Grammar**: `requirements.gra.md`

## Requirement title

**UID**: REQ-1
**Name**: Some name text.
"""

    document = SDMarkdownReader.read(doc_markdown, file_path=None)
    resolved_grammar = MarkdownGrammarReader.read(grammar_markdown)
    resolved_grammar.import_from_file = "requirements.gra.md"
    resolved_grammar.parent = document
    document.grammar = resolved_grammar

    requirement_element = resolved_grammar.elements_by_type["REQUIREMENT"]
    assert "Name" in requirement_element.fields_map

    requirement = document.section_contents[0]
    assert "Name" in requirement.ordered_fields_lookup

    output_markdown = SDMarkdownWriter.write(document)
    assert "**Name**: Some name text." in output_markdown


def test_013_markdown_grammar_reserved_field_declared_in_title_case():
    """
    The 8 reserved field roles (Title, Statement, Rationale, Comment, Level,
    Status, Tags, Prefix) back shared SDocNode accessors (reserved_title,
    reserved_statement, rationale, etc.) that hardcode the exact ALL_CAPS
    key, for the default AND any custom grammar (SDocNode has no
    per-markup subclass). A custom grammar may declare one of these fields
    using the readable surface name; it is canonicalized to the required
    internal key so that those accessors keep working, and the declared
    surface name becomes the default human title (round-tripped by the
    writer).

    Regression test: an earlier version of this canonicalization was
    reader/writer-only and left the grammar's own field.title as the
    declared surface name, which silently broke node.rationale (and
    node.reserved_statement / GrammarElement.content_field detection, which
    also hardcode "STATEMENT") for any custom grammar declaring these
    fields in a non-ALL_CAPS casing.
    """
    grammar_markdown = """\
# StrictDoc Markdown Grammar

## Element: REQUIREMENT

### Field: UID

**Type**: String
**Required**: False

### Field: Statement

**Type**: String
**Required**: False

### Field: Rationale

**Type**: String
**Required**: False
"""
    doc_markdown = """\
# Document

**Grammar**: `requirements.gra.md`

## Requirement title

**UID**: REQ-1
**Statement**: Some statement text.
**Rationale**: Some rationale text.
"""

    document = SDMarkdownReader.read(doc_markdown, file_path=None)
    resolved_grammar = MarkdownGrammarReader.read(grammar_markdown)
    resolved_grammar.import_from_file = "requirements.gra.md"
    resolved_grammar.parent = document
    document.grammar = resolved_grammar

    requirement_element = resolved_grammar.elements_by_type["REQUIREMENT"]
    # The internal key stays ALL_CAPS regardless of the declared casing.
    assert "STATEMENT" in requirement_element.fields_map
    assert "RATIONALE" in requirement_element.fields_map
    assert requirement_element.content_field == ("STATEMENT", 1)
    assert (
        requirement_element.fields_map["STATEMENT"].get_field_human_name()
        == "Statement"
    )
    assert (
        requirement_element.fields_map["RATIONALE"].get_field_human_name()
        == "Rationale"
    )

    requirement = document.section_contents[0]
    assert "STATEMENT" in requirement.ordered_fields_lookup
    assert "RATIONALE" in requirement.ordered_fields_lookup

    # The shared SDocNode accessors must actually work, not just the raw
    # field lookup (this is what the earlier, broken version got wrong).
    assert requirement.reserved_statement == "Some statement text."
    assert requirement.rationale == "Some rationale text."

    output_markdown = SDMarkdownWriter.write(document)
    assert "**Statement**: Some statement text." in output_markdown
    assert "**Rationale**: Some rationale text." in output_markdown
