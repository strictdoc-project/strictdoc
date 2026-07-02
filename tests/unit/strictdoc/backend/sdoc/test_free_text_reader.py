import pytest
from textx import TextXSyntaxError

from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.free_text import FreeTextContainer


def test_001_anchor_without_space():
    free_text_input = """
Modified statement.

[ANCHOR: AD1]!!!GARBAGE!!!
""".lstrip()

    reader = SDFreeTextReader()
    with pytest.raises(TextXSyntaxError) as exc_info:
        reader.read(free_text_input)
    assert """\
None:3:13: Expected ', ' or '\\](\\Z|\\r?\\n)' => 'NCHOR: AD1*]!!!GARBAG'\
""" == str(exc_info.value)


def test_002_anchor_without_newline_before():
    free_text_input = """
Modified statement.

!!!TEXT!!!
[ANCHOR: AD1]
""".lstrip()

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    assert len(free_text_container.parts) == 2
    assert free_text_container.parts[0] == "Modified statement.\n\n!!!TEXT!!!\n"
    assert isinstance(free_text_container.parts[1], Anchor)


def test_003_anchor_with_only_one_newline():
    free_text_input = """
Modified statement.

[ANCHOR: AD1]
!!!GARBAGE!!!
""".lstrip()

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    assert free_text_container.parts[0] == "Modified statement.\n\n"
    assert isinstance(free_text_container.parts[1], Anchor)
    assert isinstance(free_text_container.parts[2], str)
    assert free_text_container.parts[2] == "!!!GARBAGE!!!\n"


def test_010_normal_anchor_end_of_line():
    free_text_input = """
Section free text.

[ANCHOR: AD1]
""".lstrip()

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    assert free_text_container.parts[0] == "Section free text.\n\n"
    assert isinstance(free_text_container.parts[1], Anchor)


def test_011_normal_anchor_with_two_newlines():
    free_text_input = """
Modified statement.

[ANCHOR: AD1]

!!!TEXT!!!
""".lstrip()

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    assert free_text_container.parts[0] == "Modified statement.\n\n"
    assert isinstance(free_text_container.parts[1], Anchor)
    assert free_text_container.parts[2] == "\n!!!TEXT!!!\n"


def test_012_normal_anchor_end_of_line():
    free_text_input = """
Section free text.

[ANCHOR: AD1]
""".lstrip()

    reader = SDFreeTextReader()
    reader.read(free_text_input)
    free_text_container = reader.read(free_text_input)
    assert free_text_container.parts[0] == "Section free text.\n\n"
    assert isinstance(free_text_container.parts[1], Anchor)


def test_013_normal_anchor_no_other_text():
    free_text_input = """
[ANCHOR: AD1]
""".lstrip()

    reader = SDFreeTextReader()
    reader.read(free_text_input)
    free_text_container = reader.read(free_text_input)
    assert isinstance(free_text_container.parts[0], Anchor)


def test_014_two_anchors():
    free_text_input = """
Hello world

[ANCHOR: AD1, Anchor title 1]

[ANCHOR: AD2, Anchor title 2]
""".lstrip()

    reader = SDFreeTextReader()

    document = reader.read(free_text_input)
    assert isinstance(document, FreeTextContainer)

    assert document.parts[0] == "Hello world\n\n"
    assert document.parts[1].value == "AD1"
    assert document.parts[2] == "\n"
    assert document.parts[3].value == "AD2"


def test_015_anchor_lf_line_ending():
    free_text_input = "Section free text.\n\n[ANCHOR: AD1]\n"

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    assert free_text_container.parts[0] == "Section free text.\n\n"
    assert isinstance(free_text_container.parts[1], Anchor)
    assert free_text_container.parts[1].value == "AD1"


def test_016_anchor_crlf_line_ending():
    free_text_input = "Section free text.\r\n\r\n[ANCHOR: AD1]\r\n"

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    assert isinstance(free_text_container.parts[1], Anchor)
    assert free_text_container.parts[1].value == "AD1"


def test_017_anchor_title_with_quoted_comma():
    free_text_input = '[ANCHOR: AD1, "Title with, a comma"]\n'

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    anchor = free_text_container.parts[0]
    assert isinstance(anchor, Anchor)
    assert anchor.value == "AD1"
    assert anchor.title == "Title with, a comma"
    assert anchor.has_title is True


def test_018_anchor_title_with_quoted_closing_bracket():
    free_text_input = '[ANCHOR: AD1, "Title [with] brackets"]\n'

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    anchor = free_text_container.parts[0]
    assert isinstance(anchor, Anchor)
    assert anchor.value == "AD1"
    assert anchor.title == "Title [with] brackets"
    assert anchor.has_title is True


def test_019_anchor_title_with_unquoted_comma_raises():
    free_text_input = "[ANCHOR: AD1, Unquoted, comma title]\n"

    reader = SDFreeTextReader()
    with pytest.raises(TextXSyntaxError):
        reader.read(free_text_input)


def test_020_anchor_without_title_has_no_title():
    free_text_input = "[ANCHOR: AD1]\n"

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    anchor = free_text_container.parts[0]
    assert isinstance(anchor, Anchor)
    assert anchor.value == "AD1"
    assert anchor.title == "AD1"
    assert anchor.has_title is False


def test_021_link():
    free_text_input = """
Hello world [LINK: FOO] Part
""".lstrip()

    reader = SDFreeTextReader()

    document = reader.read(free_text_input)
    assert isinstance(document, FreeTextContainer)

    assert document.parts[0] == "Hello world "
    assert document.parts[1].link == "FOO"
    assert document.parts[2] == " Part\n"
