from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import Requirement, CompositeRequirement
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.backend.dsl.writer import SDWriter


def test_001_level_1_req():
    input = """
[DOCUMENT]
NAME: Test Doc

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    requirement = document.section_contents[0]
    assert requirement.ng_document_reference.get_document() == document
    assert requirement.document == document


def test_002_level_2_req():
    input = """
[DOCUMENT]
NAME: Test Doc

[SECTION]
LEVEL: 1
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

