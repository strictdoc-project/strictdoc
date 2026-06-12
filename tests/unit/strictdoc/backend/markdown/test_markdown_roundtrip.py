from typing import Optional

import pytest

from strictdoc.backend.markdown.reader import SDMarkdownReader
from strictdoc.backend.markdown.writer import SDMarkdownWriter
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.reader import SDReader


def _assert_markdown_roundtrip(
    input_markdown: str, expected_markdown: Optional[str] = None
) -> tuple[SDocDocument, str]:
    reader = SDMarkdownReader()
    document = reader.read(input_markdown, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    if expected_markdown is None:
        expected_markdown = input_markdown
    assert output_markdown == expected_markdown

    document_from_output = reader.read(output_markdown, file_path=None)
    output_markdown_2 = writer.write(document_from_output)
    assert output_markdown_2 == output_markdown

    return document, output_markdown


def _assert_sdoc_to_markdown_roundtrip(
    input_sdoc: str, expected_markdown: str
) -> str:
    document = SDReader.read(input_sdoc, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)
    assert output_markdown == expected_markdown

    _assert_markdown_roundtrip(output_markdown)
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
        entry.key: entry.value
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

    requirement_element = document.grammar.elements_by_type["REQUIREMENT"]
    assert (
        requirement_element.fields_map["RATIONALE"].human_title == "Rationale"
    )


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
**RELATIONS**:
- **Type**: Parent
  **ID**: REQ-PARENT

Child requirement statement.

## Parent with child relation

**UID**: REQ-PARENT-EXPLICIT-CHILD
**RELATIONS**:
- **Type**: Child
  **ID**: REQ-CHILD

Parent with explicit child relation.

## File relation C function

**UID**: REQ-FILE-C
**RELATIONS**:
- **Type**: File
  **Path**: file.c
  **Element**: function
  **ID**: my_function

File relation to C function.

## File relation Python class

**UID**: REQ-FILE-PY
**RELATIONS**:
- **Type**: File
  **Path**: file.py
  **Element**: class
  **ID**: MyClass

File relation to Python class.

## File relation Rust no element

**UID**: REQ-FILE-RUST
**RELATIONS**:
- **Type**: File
  **Path**: file.rs
  **ID**: my_function

File relation to Rust function without element annotation.

## File relation line range

**UID**: REQ-FILE-LINE-RANGE
**RELATIONS**:
- **Type**: File
  **Path**: file.c
  **Lines**: `10, 20`

File relation to a line range.

## Requirement with multiple relations

**UID**: REQ-MULTI
**RELATIONS**:
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

**STATEMENT**: System shall do X.
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
**STATUS**: Draft

**STATEMENT**: System shall do X.
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

**STATEMENT**: Child requirement shall do B.
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

**STATEMENT**: Parent requirement shall do A.
""",
        ),
    ],
)
def test_017_sdoc_to_markdown_roundtrip(
    input_sdoc: str, expected_markdown: str
):
    _assert_sdoc_to_markdown_roundtrip(input_sdoc, expected_markdown)
