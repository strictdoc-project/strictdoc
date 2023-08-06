from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_001_free_text():
    input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
Hello world
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_002_freetext_empty():
    input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_003_free_text_ending_free_text_not_recognized():
    input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
AAA  [/FREETEXT]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_020_free_text_inline_link():
    input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 [LINK: REQ-001] String 3
String 4
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_040_free_text_anchor_between_empty_lines():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 String 3

[ANCHOR: REQ-001, Requirements document]

String 4
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)
    assert len(document.free_texts[0].parts) == 3
    assert isinstance(document.free_texts[0].parts[1], Anchor)
    assert document.free_texts[0].parts[1].value == "REQ-001"

    assert isinstance(document.free_texts[0].parts[0], str)
    assert isinstance(document.free_texts[0].parts[2], str)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_041_free_text_anchor_start_of_free_text():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
[ANCHOR: REQ-001, Requirements document]

Test
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)
    assert len(document.free_texts[0].parts) == 2
    assert isinstance(document.free_texts[0].parts[0], Anchor)
    assert document.free_texts[0].parts[0].value == "REQ-001"

    assert isinstance(document.free_texts[0].parts[1], str)
    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_042_free_text_anchor_end_of_free_text():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 String 3

[ANCHOR: REQ-001, Requirements document]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)
    assert len(document.free_texts[0].parts) == 2
    assert isinstance(document.free_texts[0].parts[0], str)
    assert isinstance(document.free_texts[0].parts[1], Anchor)
    assert document.free_texts[0].parts[1].value == "REQ-001"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_043_free_text_anchor_between_lines():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2
[ANCHOR: REQ-001]
String 4
String 5
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)
    assert len(document.free_texts[0].parts) == 3
    assert isinstance(document.free_texts[0].parts[0], str)
    assert isinstance(document.free_texts[0].parts[1], Anchor)
    assert isinstance(document.free_texts[0].parts[2], str)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_050_free_text_anchor_inline_not_recognized():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 [ANCHOR: REQ-001] String 3
String 4
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)
    assert len(document.free_texts[0].parts) == 1
    assert isinstance(document.free_texts[0].parts[0], str)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_052_free_text_anchor_not_recognized_when_connected_to_text():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 String 3
[ANCHOR: REQ-001, Requirements document]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document: Document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    assert len(document.free_texts[0].parts) == 2
    assert isinstance(document.free_texts[0].parts[0], str)
    assert isinstance(document.free_texts[0].parts[1], Anchor)
    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_053_free_text_anchor_not_recognized_when_connected_to_text_newline_after():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 String 3
[ANCHOR: REQ-001, Requirements document]

TEST
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document: Document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    assert len(document.free_texts[0].parts) == 3
    assert isinstance(document.free_texts[0].parts[0], str)
    assert isinstance(document.free_texts[0].parts[1], Anchor)
    assert isinstance(document.free_texts[0].parts[2], str)
    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output
