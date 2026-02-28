import pytest

from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.markdown.reader import SDMarkdownReader
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import ParentReqReference


def test_001_markdown_reader_parses_root_metadata_text_and_requirement():
    markdown_content = (
        "# Document title\n"
        "\n"
        "**UID**: DOC-1 \\\n"
        "**Author**: John Doe\n"
        "\n"
        "Intro text.\n"
        "\n"
        "## Requirement title\n"
        "\n"
        "**UID**: REQ-1\n"
        "\n"
        "System shall do X.\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    assert isinstance(document, SDocDocument)
    assert document.title == "Document title"
    assert document.ng_markdown_meta_style == "backslash"
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


def test_002_markdown_reader_requires_h1_heading_first():
    markdown_content = """\
## Requirement title

**UID**: REQ-1

System shall do X.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_003_markdown_reader_rejects_content_before_h1():
    markdown_content = """\
Hello world.

# Document title
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_004_markdown_reader_rejects_second_h1():
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


def test_005_markdown_reader_rejects_forward_jump():
    markdown_content = """\
# Document

### Requirement 3

**UID**: REQ-3

Statement 3.
"""

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_006_markdown_reader_allows_backward_jump():
    markdown_content = """\
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

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    titles = [node.reserved_title for node in document.iterate_nodes()]
    assert titles == ["Req 1", "Req 3", "Req 2"]


def test_007_markdown_reader_rejects_duplicate_root_metadata_fields():
    markdown_content = "# Document title\n\n**UID**: DOC-1 \\\n**UID**: DOC-2\n"

    reader = SDMarkdownReader()
    with pytest.raises(StrictDocSemanticError):
        reader.read(markdown_content, file_path=None)


def test_008_markdown_reader_treats_invalid_root_metadata_as_text():
    markdown_content = """\
# Document title

MID: abc

Hello world.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    assert document.config.custom_metadata is None
    root_text = document.section_contents[0]
    assert isinstance(root_text, SDocNode)
    assert root_text.node_type == "TEXT"
    assert root_text.reserved_statement is not None
    assert "MID: abc" in root_text.reserved_statement
    assert "Hello world." in root_text.reserved_statement


def test_009_markdown_reader_fallbacks_to_section_and_text_for_invalid_node():
    markdown_content = """\
# Document title

## Section title

Informative text only.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section_node = document.section_contents[0]
    assert isinstance(section_node, SDocNode)
    assert section_node.node_type == "SECTION"
    assert len(section_node.section_contents) == 1

    text_node = section_node.section_contents[0]
    assert isinstance(text_node, SDocNode)
    assert text_node.node_type == "TEXT"
    assert text_node.reserved_statement is not None
    assert text_node.reserved_statement.strip() == "Informative text only."


def test_010_markdown_reader_raises_for_duplicate_fields_in_valid_node():
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


def test_011_markdown_reader_ignores_duplicate_fields_in_invalid_node():
    markdown_content = """\
# Document title

## Requirement title

**UID**: REQ-1
**UID**: REQ-2
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section_node = document.section_contents[0]
    assert isinstance(section_node, SDocNode)
    assert section_node.node_type == "SECTION"


def test_012_markdown_reader_rejects_two_empty_lines():
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


def test_013_markdown_reader_allows_two_empty_lines_in_code_block():
    markdown_content = (
        "# Document title\n"
        "\n"
        "## Requirement title\n"
        "\n"
        "**UID**: REQ-1\n"
        "\n"
        "```text\n"
        "line 1\n"
        "\n"
        "\n"
        "line 2\n"
        "```\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"


def test_014_markdown_reader_supports_bullet_meta_fields():
    markdown_content = """\
# Document title

## Requirement title

- **UID**: REQ-1
- **Status**: Draft

System shall do X.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_uid == "REQ-1"
    assert requirement.reserved_status == "Draft"
    assert document.ng_markdown_meta_style == "bullet"


def test_015_markdown_reader_supports_backslash_meta_fields():
    markdown_content = (
        "# Document title\n"
        "\n"
        "## Requirement title\n"
        "\n"
        "**UID**: REQ-1 \\\n"
        "**Status**: Draft\n"
        "\n"
        "System shall do X.\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_uid == "REQ-1"
    assert requirement.reserved_status == "Draft"
    assert document.ng_markdown_meta_style == "backslash"


def test_016_markdown_reader_supports_two_space_meta_fields():
    markdown_content = (
        "# Document title\n"
        "\n"
        "## Requirement title\n"
        "\n"
        "**UID**: REQ-1  \n"
        "**Status**: Draft  \n"
        "\n"
        "System shall do X.\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_uid == "REQ-1"
    assert requirement.reserved_status == "Draft"
    assert document.ng_markdown_meta_style == "two_spaces"


def test_017_markdown_reader_fallbacks_to_section_for_mixed_meta_styles():
    markdown_content = (
        "# Document title\n"
        "\n"
        "## Requirement title\n"
        "\n"
        "- **UID**: REQ-1\n"
        "**Status**: Draft \\\n"
        "\n"
        "System shall do X.\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    section_node = document.section_contents[0]
    assert isinstance(section_node, SDocNode)
    assert section_node.node_type == "SECTION"


def test_018_markdown_reader_supports_explicit_and_implicit_content_fields():
    markdown_content = """\
# Document title

## Requirement title

**UID**: REQ-1

System shall do X.

**Rationale**: Because it is needed.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

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


def test_019_markdown_reader_preserves_multiline_crlf_field_value():
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


def test_020_markdown_reader_treats_invalid_field_pattern_as_statement_text():
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


def test_021_markdown_reader_parses_parent_relations_field():
    markdown_content = """\
# Document title

## Child requirement

**UID**: REQ-3
**Relations**: REQ-1, REQ-2, , REQ-4

Child requirement shall do B.
"""

    reader = SDMarkdownReader()
    document = reader.read(markdown_content, file_path=None)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.node_type == "REQUIREMENT"
    assert requirement.reserved_uid == "REQ-3"
    assert len(requirement.relations) == 3
    assert all(
        isinstance(relation, ParentReqReference)
        for relation in requirement.relations
    )
    assert [relation.ref_uid for relation in requirement.relations] == [
        "REQ-1",
        "REQ-2",
        "REQ-4",
    ]
