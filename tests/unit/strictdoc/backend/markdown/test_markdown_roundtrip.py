from typing import Optional

import pytest

from strictdoc.backend.markdown.reader import SDMarkdownReader
from strictdoc.backend.markdown.writer import SDMarkdownWriter
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.helpers.exception import StrictDocException


def _assert_markdown_roundtrip(
    input_markdown: str,
    expected_markdown: Optional[str] = None,
    project_config: Optional[ProjectConfig] = None,
) -> tuple[SDocDocument, str]:
    reader = SDMarkdownReader()
    document = reader.read(
        input_markdown, file_path=None, project_config=project_config
    )

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document, project_config=project_config)

    if expected_markdown is None:
        expected_markdown = input_markdown
    assert output_markdown == expected_markdown

    document_from_output = reader.read(
        output_markdown, file_path=None, project_config=project_config
    )
    output_markdown_2 = writer.write(
        document_from_output, project_config=project_config
    )
    assert output_markdown_2 == output_markdown

    return document, output_markdown


def _assert_sdoc_to_markdown_roundtrip(
    input_sdoc: str,
    expected_markdown: str,
    project_config: Optional[ProjectConfig] = None,
) -> str:
    document = SDReader.read(input_sdoc, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document, project_config=project_config)
    assert output_markdown == expected_markdown

    _assert_markdown_roundtrip(output_markdown, project_config=project_config)
    return output_markdown


def test_001_roundtrip_canonical_markdown():
    input_markdown = """\
# Document title

**UID**: DOC-1 \\
**Author**: Jane

Intro text.

## Requirement title

**UID**: REQ-1 \\
**Status**: Draft

**Statement**: System shall do X.
"""

    _assert_markdown_roundtrip(input_markdown)


def test_002_roundtrip_normalizes_crlf_to_lf():
    input_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1

**Statement**: Line 1
""".replace("\n", "\r\n")
    expected_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1

**Statement**: Line 1
"""

    _assert_markdown_roundtrip(input_markdown, expected_markdown)


def test_003_roundtrip_root_metadata_text_and_requirement():
    input_markdown = """\
# Document title

**UID**: DOC-1 \\
**Author**: John Doe

Intro text.

## Requirement title

**UID**: REQ-1

System shall do X.
"""
    expected_markdown = """\
# Document title

**UID**: DOC-1 \\
**Author**: John Doe

Intro text.

## Requirement title

**UID**: REQ-1

**Statement**: System shall do X.
"""

    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    assert isinstance(document, SDocDocument)
    assert document.title == "Document title"
    assert document.config.markup == SDocMarkup.MARKDOWN

    assert document.config.custom_metadata is not None
    metadata = {
        entry.key: entry.get_text_value()
        for entry in document.config.custom_metadata.entries
    }
    assert metadata == {"UID": "DOC-1", "Author": "John Doe"}

    root_text = document.section_contents[0]
    assert isinstance(root_text, SDocNode)
    assert root_text.node_type == "TEXT"
    assert root_text.reserved_statement is not None
    assert root_text.reserved_statement.strip() == "Intro text."

    requirement = document.section_contents[1]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_title == "Requirement title"
    assert requirement.reserved_uid == "REQ-1"


def test_003_1_roundtrip_root_metadata_link():
    input_markdown = """\
# Document title

**UID**: DOC-1 \\
**Owner**: [LINK: REQ-1]

## Requirement title

**UID**: REQ-1

**Statement**: System shall do X.
"""

    document, _ = _assert_markdown_roundtrip(input_markdown)

    assert isinstance(document, SDocDocument)
    assert document.config.custom_metadata is not None
    owner_entry = document.config.custom_metadata.entries[-1]
    assert owner_entry.key == "Owner"
    assert len(owner_entry.parts) == 1
    assert isinstance(owner_entry.parts[0], InlineLink)
    assert owner_entry.parts[0].link == "REQ-1"

    # Regression: the parent chain must be wired so that InlineLink.parent_node()
    # (used by the incoming-links UI panel and validations) does not crash.
    assert owner_entry.get_owning_node() is document
    assert owner_entry.parts[0].parent_node() is document


def test_005_roundtrip_keeps_detected_backslash_meta_style():
    input_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1 \\
**Status**: Draft

System shall do X.
"""
    expected_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1 \\
**Status**: Draft

**Statement**: System shall do X.
"""

    _assert_markdown_roundtrip(input_markdown, expected_markdown)


def test_007_roundtrip_requirements_nested_in_three_sections():
    input_markdown = """\
# Document title

## Section A

### Section B

#### Section C

##### Requirement #1

**UID**: REQ-1

**Statement**: System shall do X.

##### Requirement #2

**UID**: REQ-2

**Statement**: System shall do Y.
"""

    _assert_markdown_roundtrip(input_markdown)


def test_008_roundtrip_allows_backward_heading_jump():
    input_markdown = """\
# Document

## Req 1

**UID**: REQ-1

Statement 1.

### Req 2

**UID**: REQ-2

Statement 2.

## Req 3

**UID**: REQ-3

Statement 3.
"""
    expected_markdown = """\
# Document

## Req 1

**UID**: REQ-1

**Statement**: Statement 1.

### Req 2

**UID**: REQ-2

**Statement**: Statement 2.

## Req 3

**UID**: REQ-3

**Statement**: Statement 3.
"""

    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    titles = [node.reserved_title for node in document.iterate_nodes()]
    assert titles == ["Req 1", "Req 3", "Req 2"]


def test_009_roundtrip_invalid_root_metadata_as_text():
    input_markdown = """\
# Document title

MID: abc

Hello world.
"""

    document, _ = _assert_markdown_roundtrip(input_markdown)

    assert document.config.custom_metadata is None
    root_text = document.section_contents[0]
    assert isinstance(root_text, SDocNode)
    assert root_text.node_type == "TEXT"
    assert root_text.reserved_statement is not None
    assert "MID: abc" in root_text.reserved_statement
    assert "Hello world." in root_text.reserved_statement


def test_010_roundtrip_invalid_node_as_section_and_text():
    input_markdown = """\
# Document title

## Section title

Informative text only.
"""

    document, _ = _assert_markdown_roundtrip(input_markdown)

    section_node = document.section_contents[0]
    assert isinstance(section_node, SDocNode)
    assert section_node.node_type == "SECTION"
    assert len(section_node.section_contents) == 1

    text_node = section_node.section_contents[0]
    assert isinstance(text_node, SDocNode)
    assert text_node.node_type == "TEXT"
    assert text_node.reserved_statement is not None
    assert text_node.reserved_statement.strip() == "Informative text only."


def test_011_roundtrip_duplicate_fields_in_invalid_node_as_section():
    input_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1
**UID**: REQ-2
"""

    document, _ = _assert_markdown_roundtrip(input_markdown)

    section_node = document.section_contents[0]
    assert isinstance(section_node, SDocNode)
    assert section_node.node_type == "SECTION"


def test_012_roundtrip_allows_two_empty_lines_in_code_block():
    input_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1

```text
line 1


line 2
```
"""
    expected_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1

**Statement**:

```text
line 1


line 2
```
"""

    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"


def test_014_roundtrip_explicit_and_implicit_content_fields():
    input_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1

System shall do X.

**Rationale**: Because it is needed.
"""
    expected_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1

**Statement**: System shall do X.

**Rationale**: Because it is needed.
"""

    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_statement is not None
    assert requirement.reserved_statement.strip() == "System shall do X."
    assert requirement.rationale == "Because it is needed."


def test_015b_roundtrip_relation_with_role():
    input_markdown = """\
# Document title

## Requirement

**UID**: REQ-3
**Relations**:
- **Type**: `Parent` \\
  **ID**: `REQ-1`
- **Type**: `Child` \\
  **ID**: `REQ-4` \\
  **Role**: `Refines`

Requirement shall do B.
"""
    expected_markdown = """\
# Document title

## Requirement

**UID**: REQ-3
**Relations**:
- **Type**: `Parent` \\
  **ID**: `REQ-1`
- **Type**: `Child` \\
  **ID**: `REQ-4` \\
  **Role**: `Refines`

**Statement**: Requirement shall do B.
"""

    _assert_markdown_roundtrip(input_markdown, expected_markdown)


def test_016_roundtrip_all_relation_types():
    input_markdown = """\
# Relations all types

## Parent requirement

**UID**: REQ-PARENT

Parent requirement statement.

## Child requirement

**UID**: REQ-CHILD
**Relations**:
- **Type**: Parent
  **ID**: REQ-PARENT

Child requirement statement.

## Parent with child relation

**UID**: REQ-PARENT-EXPLICIT-CHILD
**Relations**:
- **Type**: Child
  **ID**: REQ-CHILD

Parent with explicit child relation.

## File relation C function

**UID**: REQ-FILE-C
**Relations**:
- **Type**: File
  **Path**: file.c
  **Element**: function
  **ID**: my_function

File relation to C function.

## File relation Python class

**UID**: REQ-FILE-PY
**Relations**:
- **Type**: File
  **Path**: file.py
  **Element**: class
  **ID**: MyClass

File relation to Python class.

## File relation Rust no element

**UID**: REQ-FILE-RUST
**Relations**:
- **Type**: File
  **Path**: file.rs
  **ID**: my_function

File relation to Rust function without element annotation.

## File relation line range

**UID**: REQ-FILE-LINE-RANGE
**Relations**:
- **Type**: File
  **Path**: file.c
  **Lines**: `10, 20`

File relation to a line range.

## Requirement with multiple relations

**UID**: REQ-MULTI
**Relations**:
- **Type**: Parent
  **ID**: REQ-PARENT
- **Type**: Parent
  **ID**: REQ-PARENT-EXPLICIT-CHILD
- **Type**: File
  **Path**: file.c
  **ID**: multi_fn

Multiple relations of different types.
"""
    expected_markdown = """\
# Relations all types

## Parent requirement

**UID**: REQ-PARENT

**Statement**: Parent requirement statement.

## Child requirement

**UID**: REQ-CHILD
**Relations**:
- **Type**: `Parent` \\
  **ID**: `REQ-PARENT`

**Statement**: Child requirement statement.

## Parent with child relation

**UID**: REQ-PARENT-EXPLICIT-CHILD
**Relations**:
- **Type**: `Child` \\
  **ID**: `REQ-CHILD`

**Statement**: Parent with explicit child relation.

## File relation C function

**UID**: REQ-FILE-C
**Relations**:
- **Type**: `File` \\
  **Path**: `file.c` \\
  **Element**: `function` \\
  **ID**: `my_function`

**Statement**: File relation to C function.

## File relation Python class

**UID**: REQ-FILE-PY
**Relations**:
- **Type**: `File` \\
  **Path**: `file.py` \\
  **Element**: `class` \\
  **ID**: `MyClass`

**Statement**: File relation to Python class.

## File relation Rust no element

**UID**: REQ-FILE-RUST
**Relations**:
- **Type**: `File` \\
  **Path**: `file.rs` \\
  **ID**: `my_function`

**Statement**: File relation to Rust function without element annotation.

## File relation line range

**UID**: REQ-FILE-LINE-RANGE
**Relations**:
- **Type**: `File` \\
  **Path**: `file.c` \\
  **Lines**: `10, 20`

**Statement**: File relation to a line range.

## Requirement with multiple relations

**UID**: REQ-MULTI
**Relations**:
- **Type**: `Parent` \\
  **ID**: `REQ-PARENT`
- **Type**: `Parent` \\
  **ID**: `REQ-PARENT-EXPLICIT-CHILD`
- **Type**: `File` \\
  **Path**: `file.c` \\
  **ID**: `multi_fn`

**Statement**: Multiple relations of different types.
"""

    _assert_markdown_roundtrip(input_markdown, expected_markdown)


@pytest.mark.parametrize(
    ("input_sdoc", "expected_markdown"),
    [
        (
            """\
[DOCUMENT]
TITLE: Document title

[REQUIREMENT]
UID: REQ-1
TITLE: Requirement title
STATEMENT: System shall do X.
""",
            """\
# Document title

## Requirement title

**UID**: REQ-1

**Statement**: System shall do X.
""",
        ),
        (
            """\
[DOCUMENT]
TITLE: Document title

[REQUIREMENT]
UID: REQ-1
STATUS: Draft
TITLE: Requirement title
STATEMENT: System shall do X.
""",
            """\
# Document title

## Requirement title

**UID**: REQ-1 \\
**Status**: Draft

**Statement**: System shall do X.
""",
        ),
        (
            """\
[DOCUMENT]
TITLE: Document title

[REQUIREMENT]
UID: REQ-3
TITLE: Child requirement
STATEMENT: Child requirement shall do B.
RELATIONS:
- TYPE: Parent
  VALUE: REQ-1
- TYPE: Parent
  VALUE: REQ-2
""",
            """\
# Document title

## Child requirement

**UID**: REQ-3
**Relations**:
- **Type**: `Parent` \\
  **ID**: `REQ-1`
- **Type**: `Parent` \\
  **ID**: `REQ-2`

**Statement**: Child requirement shall do B.
""",
        ),
        (
            """\
[DOCUMENT]
TITLE: Document title

[REQUIREMENT]
UID: REQ-1
TITLE: Parent requirement
STATEMENT: Parent requirement shall do A.
RELATIONS:
- TYPE: Child
  VALUE: REQ-2
  ROLE: Refines
""",
            """\
# Document title

## Parent requirement

**UID**: REQ-1
**Relations**:
- **Type**: `Child` \\
  **ID**: `REQ-2` \\
  **Role**: `Refines`

**Statement**: Parent requirement shall do A.
""",
        ),
    ],
)
def test_017_sdoc_to_markdown_roundtrip(
    input_sdoc: str, expected_markdown: str
):
    _assert_sdoc_to_markdown_roundtrip(input_sdoc, expected_markdown)


# ---------------------------------------------------------------------------
# TYPE field tests
# ---------------------------------------------------------------------------


def test_018_type_section_input_is_parsed_as_section():
    """**Type**: SECTION in input creates a SECTION; writer drops TYPE for default grammar."""
    input_markdown = """\
# Document title

## Test Section

**Type**: SECTION
"""
    # With the default grammar, TYPE is never written back by the writer.
    expected_markdown = """\
# Document title

## Test Section
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.reserved_title == "Test Section"
    # No TEXT child: the **Type**: line must not become prose.
    assert len(section.section_contents) == 0


def test_019_type_section_with_body_strips_type_line():
    """**Type**: SECTION with a body: TYPE is dropped in output, body text is preserved."""
    input_markdown = """\
# Document title

## Test Section

**Type**: SECTION

Informative text.
"""
    expected_markdown = """\
# Document title

## Test Section

Informative text.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert len(section.section_contents) == 1

    text_node = section.section_contents[0]
    assert isinstance(text_node, SDocNode)
    assert text_node.node_type == "TEXT"
    assert text_node.reserved_statement is not None
    assert "Informative text." in text_node.reserved_statement
    # The raw **Type**: line must not appear in the text body.
    assert "**TYPE**" not in text_node.reserved_statement


def test_020_type_requirement_in_default_grammar_strips_type():
    """
    **Type**: REQUIREMENT in a default-grammar doc is accepted by the reader
    but not written back (TYPE is only emitted for custom-grammar documents).
    """
    input_markdown = """\
# Document title

## Requirement title

**Type**: REQUIREMENT \\
**UID**: REQ-1

System shall do X.
"""
    expected_markdown = """\
# Document title

## Requirement title

**UID**: REQ-1

**Statement**: System shall do X.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_uid == "REQ-1"


def test_021_type_custom_grammar_preserves_node_type():
    """Custom-grammar documents: TYPE is written for every non-SECTION/TEXT node."""
    input_markdown = """\
# Document title

**Grammar**: `requirements.gra.md`

## Some Assumption

**Type**: ASSUMPTION \\
**UID**: ASM-1

Some assumption text.
"""
    # Grammar backticks are stripped by the reader and not re-added by the
    # writer.  With an unresolved grammar (element is None) STATEMENT cannot be
    # detected as multiline, so it is serialised as a single-line meta field.
    expected_markdown = """\
# Document title

**Grammar**: requirements.gra.md

## Some Assumption

**Type**: ASSUMPTION \\
**UID**: ASM-1 \\
**Statement**: Some assumption text.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    node = document.section_contents[0]
    assert isinstance(node, SDocNode)
    assert node.node_type == "ASSUMPTION"
    assert node.reserved_title == "Some Assumption"


def test_022_type_section_emitted_in_custom_grammar():
    """
    With a custom grammar, the writer emits **Type**: SECTION for SECTION nodes.

    Without the TYPE field the reader would treat any heading that has a meta
    block (e.g. auto-generated MID) as a typed node and mis-classify it as a
    REQUIREMENT on the next read cycle.
    """
    input_markdown = """\
# Document title

**Grammar**: `requirements.gra.md`

## Test Section

**Type**: SECTION

### Some Assumption

**Type**: ASSUMPTION \\
**UID**: ASM-1

Some assumption text.
"""
    expected_markdown = """\
# Document title

**Grammar**: requirements.gra.md

## Test Section

**Type**: SECTION

### Some Assumption

**Type**: ASSUMPTION \\
**UID**: ASM-1 \\
**Statement**: Some assumption text.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.reserved_title == "Test Section"

    assumption = section.section_contents[0]
    assert isinstance(assumption, SDocNode)
    assert assumption.node_type == "ASSUMPTION"
    assert assumption.reserved_title == "Some Assumption"


def test_023_type_section_mid_preserved():
    """SECTION MID from meta block is preserved as the section's reserved_mid (MD-27)."""
    input_markdown = """\
# Document title

**Grammar**: `requirements.gra.md`

## Introduction

**Type**: SECTION \\
**MID**: 11111111111111111111111111111111

**STATEMENT**: This is a TEXT node statement, not a SECTION node statement.
"""
    expected_markdown = """\
# Document title

**Grammar**: requirements.gra.md

## Introduction

**Type**: SECTION \\
**MID**: 11111111111111111111111111111111

**STATEMENT**: This is a TEXT node statement, not a SECTION node statement.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.reserved_title == "Introduction"
    assert str(section.reserved_mid) == "11111111111111111111111111111111"
    assert section.mid_permanent is True

    text_node = section.section_contents[0]
    assert isinstance(text_node, SDocNode)
    assert text_node.node_type == "TEXT"
    statement_fields = text_node.ordered_fields_lookup.get("STATEMENT", [])
    assert len(statement_fields) > 0
    assert (
        "This is a TEXT node statement" in statement_fields[0].get_text_value()
    )


def test_024_type_section_mid_with_text_mid_body():
    r"""
    SECTION MID is preserved; **Type**: TEXT \\ **MID**: ... prefix in the section
    body is parsed as the TEXT node's machine identifier (MD-28).

    With an unresolved grammar the writer does not re-emit the TEXT TYPE/MID
    header (no TEXT element in elements_by_type), so the output contains only
    the TEXT statement.  The SECTION MID is still preserved.
    """
    input_markdown = """\
# Document title

**Grammar**: `requirements.gra.md`

## Introduction

**Type**: SECTION \\
**MID**: 11111111111111111111111111111111

**Type**: TEXT \\
**MID**: 22222222222222222222222222222222

**STATEMENT**: This is a text statement.
"""
    # With an unresolved grammar the writer cannot know that TEXT has a MID
    # field, so it emits only the statement verbatim (without TYPE/MID header).
    expected_markdown = """\
# Document title

**Grammar**: requirements.gra.md

## Introduction

**Type**: SECTION \\
**MID**: 11111111111111111111111111111111

**STATEMENT**: This is a text statement.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert str(section.reserved_mid) == "11111111111111111111111111111111"
    assert section.mid_permanent is True

    text_node = section.section_contents[0]
    assert isinstance(text_node, SDocNode)
    assert text_node.node_type == "TEXT"
    # The TEXT MID was parsed from the TYPE/MID prefix in the input body.
    assert str(text_node.reserved_mid) == "22222222222222222222222222222222"
    assert text_node.mid_permanent is True
    statement_fields = text_node.ordered_fields_lookup.get("STATEMENT", [])
    assert len(statement_fields) > 0
    assert "This is a text statement." in statement_fields[0].get_text_value()


def test_025_statement_body_with_fenced_code_block_containing_field_patterns():
    """
    A multiline STATEMENT whose body contains a fenced code block with
    **KEY**: value lines must NOT have those lines interpreted as duplicate
    field declarations.
    """
    input_markdown = """\
# Document title

## Requirement with code-block example

**UID**: REQ-1

**Statement**:

The heading meta block uses the following syntax:

```
**Type**: SECTION \\
**MID**: 11111111111111111111111111111111
```

A second example shows the TEXT prefix:

```
**Type**: TEXT \\
**MID**: 22222222222222222222222222222222

**Statement**: Body text here.
```
"""
    reader = SDMarkdownReader()
    # This currently raises StrictDocSemanticError due to duplicate field
    # names found inside the fenced code blocks.
    document = reader.read(input_markdown, file_path=None)

    req = document.section_contents[0]
    assert isinstance(req, SDocNode)
    statement_fields = req.ordered_fields_lookup.get("STATEMENT", [])
    assert len(statement_fields) == 1


def test_026_document_level_prefix_roundtrips():
    """Document-level PREFIX is preserved across read/write cycles."""
    input_markdown = """\
# Requirements specification

**Prefix**: MYDOC-

## Requirement

**UID**: MYDOC-001

**Statement**: System shall do B.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown)
    assert document.config.requirement_prefix == "MYDOC-"


def test_027_section_prefix_without_type_roundtrips():
    """Section-level PREFIX (no explicit TYPE) is preserved across read/write cycles."""
    input_markdown = """\
# Requirements specification

## Chapter 2

**Prefix**: LEVEL2-REQ-

### Requirement

**UID**: LEVEL2-REQ-001

**Statement**: System shall do B.
"""
    document, output = _assert_markdown_roundtrip(input_markdown)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.get_prefix() == "LEVEL2-REQ-"
    # No spurious TEXT child from the meta block.
    assert not any(
        n.node_type == "TEXT"
        for n in section.section_contents
        if isinstance(n, SDocNode)
    )


def test_028_section_prefix_with_type_drops_type_on_output():
    """
    Section-level PREFIX written with explicit TYPE: SECTION is accepted;
    the writer drops TYPE on output for default-grammar documents (matches
    the existing TYPE: SECTION normalisation behaviour).
    """
    input_markdown = """\
# Requirements specification

## Chapter 2

**Type**: SECTION \\
**Prefix**: LEVEL2-REQ-

### Requirement

**UID**: LEVEL2-REQ-001

**Statement**: System shall do B.
"""
    expected_markdown = """\
# Requirements specification

## Chapter 2

**Prefix**: LEVEL2-REQ-

### Requirement

**UID**: LEVEL2-REQ-001

**Statement**: System shall do B.
"""
    document, _ = _assert_markdown_roundtrip(input_markdown, expected_markdown)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.get_prefix() == "LEVEL2-REQ-"


def test_029_roundtrip_headings_deeper_than_h6():
    input_sdoc = """\
[DOCUMENT]
TITLE: Document title

[[SECTION]]
TITLE: Level 1

[[SECTION]]
TITLE: Level 2

[[SECTION]]
TITLE: Level 3

[[SECTION]]
TITLE: Level 4

[[SECTION]]
TITLE: Level 5

[[SECTION]]
TITLE: Level 6

[REQUIREMENT]
UID: REQ-DEEP-1
TITLE: Deep requirement
STATEMENT: Statement nested seven levels below the document.

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]
"""
    expected_markdown = """\
# Document title

## Level 1

### Level 2

#### Level 3

##### Level 4

###### Level 5

####### Level 6

######## Deep requirement

**UID**: REQ-DEEP-1

**Statement**: Statement nested seven levels below the document.
"""
    project_config = ProjectConfig(
        project_features=[ProjectFeature.MARKDOWN_DEEP_HEADINGS]
    )
    _assert_sdoc_to_markdown_roundtrip(
        input_sdoc, expected_markdown, project_config=project_config
    )


def test_030_writer_rejects_deep_document_without_feature_flag():
    input_sdoc = """\
[DOCUMENT]
TITLE: Document title

[[SECTION]]
TITLE: Level 1

[[SECTION]]
TITLE: Level 2

[[SECTION]]
TITLE: Level 3

[[SECTION]]
TITLE: Level 4

[[SECTION]]
TITLE: Level 5

[[SECTION]]
TITLE: Level 6

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]
"""
    document = SDReader.read(input_sdoc, file_path=None)

    writer = SDMarkdownWriter()
    with pytest.raises(StrictDocException) as exc_info:
        writer.write(document)
    assert "MARKDOWN_DEEP_HEADINGS" in str(exc_info.value)
