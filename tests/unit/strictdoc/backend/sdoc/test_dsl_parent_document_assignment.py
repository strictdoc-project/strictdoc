from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.helpers.cast import assert_cast


def test_001_level_1_req():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    requirement = assert_cast(document.section_contents[0], SDocNode)
    assert requirement.ng_document_reference.get_document() == document
    assert requirement.get_document() == document


def test_002_level_2_req():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Section 1

[REQUIREMENT]

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    section = assert_cast(document.section_contents[0], SDocSection)
    req: SDocNode = assert_cast(section.section_contents[0], SDocNode)
    assert req.ng_document_reference.get_document() == document
    assert req.get_document() == document
