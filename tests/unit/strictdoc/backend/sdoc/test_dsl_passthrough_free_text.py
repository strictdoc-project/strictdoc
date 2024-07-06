from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_001_free_text(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
Hello world
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_002_freetext_empty(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_003_free_text_ending_free_text_not_recognized(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
AAA  [/FREETEXT]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_004_section_free_text(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Section

[FREETEXT]
Hello world
[/FREETEXT]

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_020_free_text_inline_link(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 [LINK: REQ-001] String 3
String 4
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_040_free_text_anchor_between_empty_lines(default_project_config):
    input_sdoc = """
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

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)
    text_node: SDocNode = document.section_contents[0]
    content_field: SDocNodeField = text_node.get_content_field()
    assert len(content_field.parts) == 3
    assert isinstance(content_field.parts[1], Anchor)
    assert content_field.parts[1].value == "REQ-001"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_041_free_text_anchor_start_of_free_text(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
[ANCHOR: REQ-001, Requirements document]

Test
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)
    text_node: SDocNode = document.section_contents[0]
    content_field: SDocNodeField = text_node.get_content_field()
    assert len(content_field.parts) == 2
    assert isinstance(content_field.parts[0], Anchor)
    assert content_field.parts[0].value == "REQ-001"

    assert isinstance(content_field.parts[1], str)
    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_042_two_anchors(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Document 1

[TEXT]
STATEMENT: >>>
Modified text

[ANCHOR: AD1, Anchor title 1]

[ANCHOR: AD2, Anchor title 2]
<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_042_free_text_anchor_end_of_free_text(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 String 3

[ANCHOR: REQ-001, Requirements document]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)
    text_node: SDocNode = document.section_contents[0]
    content_field: SDocNodeField = text_node.get_content_field()
    assert len(content_field.parts) == 2
    assert isinstance(content_field.parts[0], str)
    assert isinstance(content_field.parts[1], Anchor)
    assert content_field.parts[1].value == "REQ-001"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_043_free_text_anchor_between_lines(default_project_config):
    input_sdoc = """
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

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)
    text_node: SDocNode = document.section_contents[0]
    content_field: SDocNodeField = text_node.get_content_field()
    assert len(content_field.parts) == 3
    assert isinstance(content_field.parts[0], str)
    assert isinstance(content_field.parts[1], Anchor)
    assert isinstance(content_field.parts[2], str)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_050_free_text_anchor_inline_not_recognized(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 [ANCHOR: REQ-001] String 3
String 4
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)
    text_node: SDocNode = document.section_contents[0]
    content_field: SDocNodeField = text_node.get_content_field()
    assert len(content_field.parts) == 1
    assert isinstance(content_field.parts[0], str)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_052_free_text_anchor_not_recognized_when_connected_to_text(
    default_project_config,
):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
String 1
String 2 String 3
[ANCHOR: REQ-001, Requirements document]
[/FREETEXT]
""".lstrip()

    reader = SDReader()

    document: SDocDocument = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)
    text_node: SDocNode = document.section_contents[0]
    content_field: SDocNodeField = text_node.get_content_field()
    assert len(content_field.parts) == 2
    assert isinstance(content_field.parts[0], str)
    assert isinstance(content_field.parts[1], Anchor)
    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_053_free_text_anchor_not_recognized_when_connected_to_text_newline_after(
    default_project_config,
):
    input_sdoc = """
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

    document: SDocDocument = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)
    text_node: SDocNode = document.section_contents[0]
    content_field: SDocNodeField = text_node.get_content_field()
    assert len(content_field.parts) == 3
    assert isinstance(content_field.parts[0], str)
    assert isinstance(content_field.parts[1], Anchor)
    assert isinstance(content_field.parts[2], str)
    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output
