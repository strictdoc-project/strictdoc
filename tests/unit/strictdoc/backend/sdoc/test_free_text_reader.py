import pytest
from textx import TextXSyntaxError

from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.free_text import FreeText


def test_001_anchor_without_space():
    free_text_input = """
Modified statement.

[ANCHOR: AD1]!!!GARBAGE!!!
""".lstrip()

    reader = SDFreeTextReader()
    with pytest.raises(TextXSyntaxError) as exc_info:
        reader.read(free_text_input)
    assert """\
None:3:14: \
Expected '\\Z|(\\n(\\n|\\Z|(?=\\[\\/FREETEXT\\])))' => 'CHOR: AD1]*!!!GARBAGE'\
""" == str(
        exc_info.value
    )


def test_002_anchor_without_newline_before():
    """
    The expectation here is that the anchor does not get recognized at all.
    """

    free_text_input = """
Modified statement.

!!!GARBAGE!!!
[ANCHOR: AD1]
""".lstrip()

    reader = SDFreeTextReader()
    free_text_container = reader.read(free_text_input)
    assert (
        free_text_container.parts[0]
        == "Modified statement.\n\n!!!GARBAGE!!!\n[ANCHOR: AD1]\n"
    )


def test_003_anchor_with_only_one_newline():
    free_text_input = """
Modified statement.

[ANCHOR: AD1]
!!!GARBAGE!!!
""".lstrip()

    reader = SDFreeTextReader()
    with pytest.raises(TextXSyntaxError) as exc_info:
        reader.read(free_text_input)
    assert (
        str(exc_info.value)
        == """\
None:3:14: \
Expected '\\Z|(\\n(\\n|\\Z|(?=\\[\\/FREETEXT\\])))' => 'CHOR: AD1]* !!!GARBAG'\
"""
    )


def test_010_normal_anchor_end_of_line():
    free_text_input = """
Section free text.

[ANCHOR: AD1]\
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
    assert free_text_container.parts[2] == "!!!TEXT!!!\n"


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


def test_020_link():
    free_text_input = """
Hello world [LINK: FOO] Part
""".lstrip()

    reader = SDFreeTextReader()

    document = reader.read(free_text_input)
    assert isinstance(document, FreeText)

    assert document.parts[0] == "Hello world "
    assert document.parts[1].link == "FOO"
    assert document.parts[2] == " Part\n"
