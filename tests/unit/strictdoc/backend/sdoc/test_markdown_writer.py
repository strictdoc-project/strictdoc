from strictdoc.backend.sdoc.markdown.reader import SDMarkdownReader
from strictdoc.backend.sdoc.markdown.writer import SDMarkdownWriter
from strictdoc.backend.sdoc.reader import SDReader


def test_001_markdown_writer_roundtrip_lf_for_canonical_markdown():
    input_markdown = (
        "# Document title\n"
        "\n"
        "**UID**: DOC-1 \\\n"
        "**Author**: Jane\n"
        "\n"
        "Intro text.\n"
        "\n"
        "## Requirement title\n"
        "\n"
        "**UID**: REQ-1 \\\n"
        "**Status**: Draft\n"
        "\n"
        "**Statement**: System shall do X.\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(input_markdown, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    assert output_markdown == input_markdown


def test_002_markdown_writer_normalizes_crlf_to_lf():
    input_markdown = (
        "# Document title\r\n"
        "\r\n"
        "## Requirement title\r\n"
        "\r\n"
        "**UID**: REQ-1\r\n"
        "\r\n"
        "**Statement**: Line 1\r\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(input_markdown, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    assert "\r" not in output_markdown
    assert output_markdown == (
        "# Document title\n"
        "\n"
        "## Requirement title\n"
        "\n"
        "**UID**: REQ-1\n"
        "\n"
        "**Statement**: Line 1\n"
    )


def test_003_markdown_writer_keeps_detected_meta_style():
    input_markdown = """\
# Document title

## Requirement title

- **UID**: REQ-1
- **Status**: Draft

System shall do X.
"""

    reader = SDMarkdownReader()
    document = reader.read(input_markdown, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    assert "- **UID**: REQ-1" in output_markdown
    assert "- **Status**: Draft" in output_markdown


def test_004_markdown_writer_serializes_sdoc_document():
    input_sdoc = """\
[DOCUMENT]
TITLE: Document title

[REQUIREMENT]
UID: REQ-1
TITLE: Requirement title
STATEMENT: System shall do X.
"""

    document = SDReader.read(input_sdoc, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    assert output_markdown.startswith("# Document title\n")
    assert "## Requirement title" in output_markdown
    assert "**UID**: REQ-1" in output_markdown
    assert "**STATEMENT**: System shall do X." in output_markdown


def test_005_markdown_writer_uses_backslash_style_for_new_documents():
    input_sdoc = """\
[DOCUMENT]
TITLE: Document title

[REQUIREMENT]
UID: REQ-1
STATUS: Draft
TITLE: Requirement title
STATEMENT: System shall do X.
"""

    document = SDReader.read(input_sdoc, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    assert "**UID**: REQ-1 \\" in output_markdown
    assert "**STATUS**: Draft" in output_markdown


def test_006_markdown_writer_supports_requirements_nested_in_three_sections():
    input_markdown = (
        "# Document title\n"
        "\n"
        "## Section A\n"
        "\n"
        "### Section B\n"
        "\n"
        "#### Section C\n"
        "\n"
        "##### Requirement #1\n"
        "\n"
        "**UID**: REQ-1\n"
        "\n"
        "**Statement**: System shall do X.\n"
        "\n"
        "##### Requirement #2\n"
        "\n"
        "**UID**: REQ-2\n"
        "\n"
        "**Statement**: System shall do Y.\n"
    )

    reader = SDMarkdownReader()
    document = reader.read(input_markdown, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    assert output_markdown == input_markdown


def test_007_markdown_writer_serializes_parent_relations_field():
    input_sdoc = """\
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
"""

    document = SDReader.read(input_sdoc, file_path=None)

    writer = SDMarkdownWriter()
    output_markdown = writer.write(document)

    assert "**UID**: REQ-3 \\" in output_markdown
    assert "**Relations**: REQ-1, REQ-2" in output_markdown
