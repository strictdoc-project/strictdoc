from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.reader import SDReader


def test_001_level_1_req():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    requirement = document.section_contents[0]
    assert requirement.ng_document_reference.get_document() == document
    assert requirement.document == document


def test_002_level_2_req():
    input = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Section 1

[REQUIREMENT]

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    section = document.section_contents[0]
    req = section.section_contents[0]
    assert req.ng_document_reference.get_document() == document
    assert req.document == document
