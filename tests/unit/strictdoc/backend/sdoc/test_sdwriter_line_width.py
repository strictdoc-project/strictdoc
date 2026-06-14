"""
Tests for SDWriter line-width formatting (document_line_width config option).
"""

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.project_config import ProjectConfig


def _make_project_config(line_width: int) -> ProjectConfig:
    config = ProjectConfig()
    config.document_line_width = line_width
    return config


def test_sdwriter_no_wrap_when_line_width_not_set(default_project_config):
    long_line = "A" * 100
    input_sdoc = f"""\
[DOCUMENT]
TITLE: Test

[TEXT]
STATEMENT: >>>
{long_line}
<<<
"""
    reader = SDReader()
    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)
    assert long_line in output


def test_sdwriter_wraps_long_paragraph():
    # 100-char line that should be wrapped at 80
    long_line = "word " * 20  # 100 chars
    input_sdoc = f"""\
[DOCUMENT]
TITLE: Test

[TEXT]
STATEMENT: >>>
{long_line.strip()}
<<<
"""
    reader = SDReader()
    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    config = _make_project_config(80)
    writer = SDWriter(config)
    output = writer.write(document)

    statement_start = output.index("STATEMENT: >>>\n") + len("STATEMENT: >>>\n")
    statement_end = output.index("\n<<<", statement_start)
    statement_content = output[statement_start:statement_end]

    for line in statement_content.split("\n"):
        assert len(line) <= 80, f"Line exceeds 80 chars: {line!r}"


def test_sdwriter_preserves_short_lines():
    input_sdoc = """\
[DOCUMENT]
TITLE: Test

[TEXT]
STATEMENT: >>>
Short line.

Another short line.
<<<
"""
    reader = SDReader()
    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    config = _make_project_config(80)
    writer = SDWriter(config)
    output = writer.write(document)

    assert "Short line." in output
    assert "Another short line." in output


def test_sdwriter_preserves_list_paragraphs():
    input_sdoc = """\
[DOCUMENT]
TITLE: Test

[TEXT]
STATEMENT: >>>
- Item one that is quite long and goes beyond the eighty character line width limit set
- Item two that is also quite long and goes beyond the eighty character line width limit
<<<
"""
    reader = SDReader()
    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    config = _make_project_config(80)
    writer = SDWriter(config)
    output = writer.write(document)

    # List items should NOT be wrapped (structured content)
    assert "- Item one that is quite long" in output
    assert "- Item two that is also quite long" in output
