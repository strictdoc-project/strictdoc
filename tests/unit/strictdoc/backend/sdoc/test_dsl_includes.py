import pytest
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    CompositeRequirement,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.reader import SDIReader


@pytest.fixture
def fake_filesystem(fs):  # pylint:disable=invalid-name
    """Variable name 'fs' causes a pylint warning. Provide a longer name
    acceptable to pylint for use in tests.
    """
    yield fs


def test_000_reference():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]

[SECTION]
TITLE: Section 1

[REQUIREMENT]
STATEMENT: Sub requirement

[COMPOSITE_REQUIREMENT]
STATEMENT: Composite requirement

[REQUIREMENT]
STATEMENT: Sub sub requirement

[/COMPOSITE_REQUIREMENT]

[/SECTION]
    """.lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    validate_document(document)


def validate_document(document):
    assert isinstance(document, Document)

    requirement = document.section_contents[0]
    assert isinstance(requirement, Requirement)
    assert requirement.ng_document_reference.get_document() == document
    assert requirement.document == document
    assert requirement.ng_level == 1

    section = document.section_contents[1]
    assert isinstance(section, Section)
    assert section.title == "Section 1"
    assert section.ng_level == 1

    sub_requirement = section.section_contents[0]
    assert isinstance(sub_requirement, Requirement)
    assert sub_requirement.ng_level == 2

    composite_requirement = section.section_contents[1]
    assert isinstance(composite_requirement, CompositeRequirement)
    assert composite_requirement.ng_level == 2

    sub_sub_requirement = composite_requirement.requirements[0]
    assert isinstance(sub_sub_requirement, Requirement)
    assert sub_sub_requirement.ng_level == 3


def test_001_load_fragment_from_document(fake_filesystem):
    fake_filesystem.create_file(
        "test_fragment.ssec",
        contents="""
[FRAGMENT]

[SECTION]
TITLE: Section 1

[REQUIREMENT]
STATEMENT: Sub requirement

[COMPOSITE_REQUIREMENT]
STATEMENT: Composite requirement

[REQUIREMENT]
STATEMENT: Sub sub requirement

[/COMPOSITE_REQUIREMENT]

[/SECTION]
""".lstrip(),
    )

    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]

[INCLUDE_SECTION_FROM_FILE]
FILE: test_fragment.ssec

""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    validate_document(document)


def test_002_load_both(fake_filesystem):
    fake_filesystem.create_file(
        "test_fragment.ssec",
        contents="""
[FRAGMENT]

[SECTION]
TITLE: Section 1

[REQUIREMENT]
STATEMENT: Sub requirement

[COMPOSITE_REQUIREMENT]
STATEMENT: Composite requirement

[REQUIREMENT]
STATEMENT: Sub sub requirement

[/COMPOSITE_REQUIREMENT]

[/SECTION]
""".lstrip(),
    )

    fake_filesystem.create_file(
        "input.sdoc",
        contents="""
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]

[INCLUDE_SECTION_FROM_FILE]
FILE: test_fragment.ssec

""".lstrip(),
    )

    reader = SDReader()

    document = reader.read_from_file("input.sdoc")
    validate_document(document)
