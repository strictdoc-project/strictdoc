import pytest

from strictdoc.backend.markdown.reader import SDMarkdownReader
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.node import SDocNode


def test_001_markdown_reader_requires_h1_heading_first():
    markdown_content = """\
## Requirement title

**UID**: REQ-1

System shall do X.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_002_markdown_reader_rejects_content_before_h1():
    markdown_content = """\
Hello world.

# Document title
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_003_markdown_reader_rejects_second_h1():
    markdown_content = """\
# Document title

## Requirement 1

**UID**: REQ-1

Statement 1.

# Another root
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_004_markdown_reader_rejects_forward_jump():
    markdown_content = """\
# Document

### Requirement 3

**UID**: REQ-3

Statement 3.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_005_markdown_reader_rejects_duplicate_root_metadata_fields():
    markdown_content = "# Document title\n\n**UID**: DOC-1 \\\n**UID**: DOC-2\n"

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_006_markdown_reader_raises_for_duplicate_fields_in_valid_node():
    markdown_content = """\
# Document title

## Requirement title

**UID**: REQ-1
**UID**: REQ-2

System shall do X.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_007_markdown_reader_rejects_two_empty_lines():
    markdown_content = """\
# Document title

## Requirement title

**UID**: REQ-1

Line 1.


Line 2.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_008_markdown_reader_raises_error_on_missing_relation_type_key():
    markdown_content = """\
# Document title

## Requirement

**UID**: REQ-1
**Relations**:
- **ID**: `REQ-0`

Requirement shall do A.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError) as exc_info:
        reader.read(markdown_content, file_path=None)
    assert "Type" in exc_info.value.title


def test_009_markdown_reader_raises_error_on_unknown_relation_type():
    markdown_content = """\
# Document title

## Requirement

**UID**: REQ-1
**Relations**:
- **Type**: `Unknown` \\
  **ID**: `REQ-0`

Requirement shall do A.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError) as exc_info:
        reader.read(markdown_content, file_path=None)
    assert "Unknown" in exc_info.value.title


def test_010_markdown_reader_raises_error_on_missing_id_key():
    markdown_content = """\
# Document title

## Requirement

**UID**: REQ-1
**Relations**:
- **Type**: `Parent`

Requirement shall do A.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError) as exc_info:
        reader.read(markdown_content, file_path=None)
    assert "ID" in exc_info.value.title


def test_011_markdown_reader_raises_error_on_unknown_key_in_relation():
    markdown_content = """\
# Document title

## Requirement

**UID**: REQ-1
**Relations**:
- **Type**: `Parent` \\
  **ID**: `REQ-0` \\
  **Bogus**: `value`

Requirement shall do A.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError) as exc_info:
        reader.read(markdown_content, file_path=None)
    assert "Bogus" in exc_info.value.title


def test_012_markdown_reader_preserves_multiline_crlf_field_value():
    markdown_content = (
        "# Document title\r\n"
        "\r\n"
        "## Requirement title\r\n"
        "\r\n"
        "**UID**: REQ-1\r\n"
        "\r\n"
        "**Statement**:\r\n"
        "\r\n"
        "Line 1\r\n"
        "Line 2\r\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_statement == "Line 1\r\nLine 2\r\n"


def test_013_markdown_reader_treats_invalid_field_pattern_as_statement_text():
    markdown_content = """\
# Document title

## Requirement title

**UID**: REQ-1

**BAD.NAME**: value
System shall do X.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_statement is not None
    assert "**BAD.NAME**: value" in requirement.reserved_statement


def test_014_rejects_blank_line_between_meta_and_relations():
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

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError) as exc_info:
        reader.read(input_markdown, file_path=None)
    assert "Relations must directly follow" in exc_info.value.title


def test_015_document_level_prefix_sets_requirement_prefix():
    markdown_content = """\
# Requirements specification

**PREFIX**: MYDOC-

## Requirement

**UID**: MYDOC-001

System shall do B.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    assert document.config.requirement_prefix == "MYDOC-"


def test_016_section_level_prefix_is_stored_on_section_node():
    markdown_content = """\
# Requirements specification

## Chapter 2

**TYPE**: SECTION \\
**PREFIX**: LEVEL2-REQ-

### Requirement

**UID**: LEVEL2-REQ-001

System shall do B.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.get_prefix() == "LEVEL2-REQ-"


def test_017_section_immediately_followed_by_child_section_has_no_empty_text_node():
    # Regression: a blank line between a section heading and its first child
    # heading was captured as the section body ("\n"), which passed the
    # `len > 0` guard and produced a spurious empty TEXT node.
    markdown_content = """\
# Document title

## Parent section

### Child section

**MID**: aabbccdd11223344aabbccdd11223344 \\
**UID**: REQ-1

**Statement**: Some statement.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    parent_section = document.section_contents[0]
    assert isinstance(parent_section, SDocNode)
    assert parent_section.node_type == "SECTION"
    # Must contain only the child requirement, no spurious empty TEXT node.
    assert len(parent_section.section_contents) == 1
    child = parent_section.section_contents[0]
    assert isinstance(child, SDocNode)
    assert child.node_type == "REQUIREMENT"
