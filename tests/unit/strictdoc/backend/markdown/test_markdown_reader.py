import pytest

from strictdoc.backend.markdown.reader import SDMarkdownReader
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.inline_link import InlineLink
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
        "**STATEMENT**:\r\n"
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

**Prefix**: MYDOC-

## Requirement

**UID**: MYDOC-001

System shall do B.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    assert document.config.requirement_prefix == "MYDOC-"


def test_016_link_tag_in_statement_creates_inline_link_part():
    markdown_content = """\
# Document

## Requirement A

**UID**: REQ-1

System shall do X. See also [LINK: REQ-2].
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    stmt_field = requirement.ordered_fields_lookup["STATEMENT"][0]
    inline_link_parts = [
        p for p in stmt_field.parts if isinstance(p, InlineLink)
    ]
    assert len(inline_link_parts) == 1
    assert inline_link_parts[0].link == "REQ-2"
    assert inline_link_parts[0].parent is stmt_field
    assert stmt_field.parent is requirement


def test_017_anchor_tag_in_statement_creates_anchor_part():
    markdown_content = """\
# Document

## Section

[ANCHOR: SEC-INTRO]
This section describes the introduction.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    text_node = section.section_contents[0]
    assert isinstance(text_node, SDocNode)
    stmt_field = text_node.ordered_fields_lookup["STATEMENT"][0]
    anchor_parts = [p for p in stmt_field.parts if isinstance(p, Anchor)]
    assert len(anchor_parts) == 1
    assert anchor_parts[0].value == "SEC-INTRO"
    assert anchor_parts[0].parent is stmt_field
    assert stmt_field.parent is text_node


def test_018_anchor_tag_with_title_creates_anchor_with_title():
    markdown_content = """\
# Document

## Section

[ANCHOR: SEC-INTRO, Introduction]
This section describes the introduction.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section = document.section_contents[0]
    text_node = section.section_contents[0]
    stmt_field = text_node.ordered_fields_lookup["STATEMENT"][0]
    anchor_parts = [p for p in stmt_field.parts if isinstance(p, Anchor)]
    assert len(anchor_parts) == 1
    assert anchor_parts[0].value == "SEC-INTRO"
    assert anchor_parts[0].title == "Introduction"
    assert anchor_parts[0].has_title is True


def test_019_link_tag_in_requirement_statement_wires_parent_correctly():
    markdown_content = """\
# Document

## Requirement

**UID**: REQ-1

Statement with [LINK: SOME-ANCHOR] inline.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    stmt_field = requirement.ordered_fields_lookup["STATEMENT"][0]
    inline_links = [p for p in stmt_field.parts if isinstance(p, InlineLink)]
    assert len(inline_links) == 1
    link = inline_links[0]
    assert link.link == "SOME-ANCHOR"
    # parent chain: InlineLink -> SDocNodeField -> SDocNode
    assert link.parent is stmt_field
    assert link.parent_node() is requirement


def test_020_link_tag_inside_inline_code_span_is_not_parsed():
    # [LINK: ...] inside backtick code spans must be treated as plain text,
    # not as InlineLink objects (the referenced UID may not exist).
    markdown_content = """\
# Document

## Requirement

**UID**: MD-1

A `[LINK: NONEXISTENT]` token is written like this.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    stmt_field = requirement.ordered_fields_lookup["STATEMENT"][0]
    inline_links = [p for p in stmt_field.parts if isinstance(p, InlineLink)]
    assert len(inline_links) == 0
    full_text = "".join(
        p if isinstance(p, str) else "" for p in stmt_field.parts
    )
    assert "[LINK: NONEXISTENT]" in full_text


def test_021_link_tag_inside_fenced_code_block_is_not_parsed():
    # [LINK: ...] inside a fenced code block must not become an InlineLink.
    markdown_content = """\
# Document

## Requirement

**UID**: MD-1

Example usage:

```markdown
See also [LINK: NONEXISTENT].
```
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    stmt_field = requirement.ordered_fields_lookup["STATEMENT"][0]
    inline_links = [p for p in stmt_field.parts if isinstance(p, InlineLink)]
    assert len(inline_links) == 0


def test_022_link_tag_outside_code_is_still_parsed_when_code_also_present():
    # [LINK: REAL] outside a code fence must still become an InlineLink even
    # when there is also a [LINK: FAKE] inside a fenced code block.
    markdown_content = """\
# Document

## Requirement

**UID**: MD-1

See [LINK: REAL-1] for details.

```markdown
Do NOT parse [LINK: FAKE].
```
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    stmt_field = requirement.ordered_fields_lookup["STATEMENT"][0]
    inline_links = [p for p in stmt_field.parts if isinstance(p, InlineLink)]
    assert len(inline_links) == 1
    assert inline_links[0].link == "REAL-1"


def test_023_anchor_tag_inside_inline_code_span_is_not_parsed():
    # [ANCHOR: ...] inside a backtick span must not become an Anchor object.
    markdown_content = """\
# Document

## Section

Use `[ANCHOR: FAKE-ANCHOR]` to place an anchor.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    text_node = section.section_contents[0]
    stmt_field = text_node.ordered_fields_lookup["STATEMENT"][0]
    anchors = [p for p in stmt_field.parts if isinstance(p, Anchor)]
    assert len(anchors) == 0


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

**STATEMENT**: Some statement.
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


def test_024_markdown_reader_registers_document_config():
    markdown_content = """\
# Document title

**UID**: DOC-1 \\
**Version**: Git commit: @GIT_VERSION, Git branch: @GIT_BRANCH \\
**Date**: @GIT_COMMIT_DATETIME \\
**Classification**: Confidential
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    assert document.config.uid == "DOC-1"
    assert (
        document.config.version
        == "Git commit: @GIT_VERSION, Git branch: @GIT_BRANCH"
    )
    assert document.config.date == "@GIT_COMMIT_DATETIME"
    assert document.config.classification == "Confidential"
    assert document.config.get_custom_metadata() == []


def test_026_markdown_reader_registers_document_metadata():
    markdown_content = """\
# Document title

**Author**: Jane \\
**Checked-by**: Chuck Norris
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    assert document.config.get_custom_metadata() == [
        ("Author", "Jane"),
        ("Checked-by", "Chuck Norris"),
    ]


def test_025_markdown_reader_empty_heading_produces_no_title_field():
    markdown_content = """\
# Document title

##

**Type**: REQUIREMENT \\
**UID**: REQ-1
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_uid == "REQ-1"
    assert requirement.reserved_title is None
    assert "TITLE" not in requirement.ordered_fields_lookup


def test_027_section_level_fields():
    markdown_content = """\
# Document title

## Chapter 2

**Type**: SECTION \\
**MID**: aabbccdd11223344aabbccdd11223344 \\
**UID**: SEC-1 \\
**PREFIX**: LEVEL2-REQ-

Some prose.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.reserved_uid == "SEC-1"
    assert str(section.reserved_mid) == "aabbccdd11223344aabbccdd11223344"
    assert section.get_prefix() == "LEVEL2-REQ-"
    assert list(section.ordered_fields_lookup.keys()) == [
        "MID",
        "UID",
        "PREFIX",
        "TITLE",
    ]


def test_028_section_level_uid_without_explicit_type_has_no_duplicated_prose():
    markdown_content = """\
# Document title

## Chapter 2

**UID**: SEC-1

### Notes

Some prose.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.node_type == "SECTION"
    assert section.reserved_uid == "SEC-1"
    assert [c.node_type for c in section.section_contents] == ["SECTION"]
