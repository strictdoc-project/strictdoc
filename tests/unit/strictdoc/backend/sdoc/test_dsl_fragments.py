import pytest

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.fragment_from_file import FragmentFromFile
from strictdoc.backend.sdoc.models.node import (
    CompositeRequirement,
    SDocNode,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


@pytest.fixture
def fake_filesystem(fs):  # pylint:disable=invalid-name
    """Variable name 'fs' causes a pylint warning. Provide a longer name
    acceptable to pylint for use in tests.
    """
    yield fs


def test_001_load_from_files(fake_filesystem):
    fragment_content = """\
[FRAGMENT]

[SECTION]
TITLE: Section 1

[FREETEXT]

Things

[/FREETEXT]

[REQUIREMENT]
STATEMENT: Sub requirement

[COMPOSITE_REQUIREMENT]
STATEMENT: Composite requirement

[REQUIREMENT]
STATEMENT: Sub sub requirement

[/COMPOSITE_REQUIREMENT]

[/SECTION]

[REQUIREMENT]
"""

    fake_filesystem.create_file(
        "test_fragment.ssec",
        contents=fragment_content,
    )

    """
    Main document fixture.
    """

    document_content = """\
[DOCUMENT]
TITLE: Test Doc

[FREETEXT]
Stuff
[/FREETEXT]

[FRAGMENT_FROM_FILE]
FILE: test_fragment.ssec

[COMPOSITE_REQUIREMENT]
TITLE: After fragment composite requirement.

[REQUIREMENT]

[/COMPOSITE_REQUIREMENT]
"""
    fake_filesystem.create_file("input.sdoc", contents=document_content)

    reader = SDReader()

    document = reader.read_from_file("input.sdoc")
    assert isinstance(document, SDocDocument)
    assert len(document.free_texts) == 1

    fragment_from_file: FragmentFromFile = document.section_contents[0]
    assert isinstance(fragment_from_file, FragmentFromFile)

    assert fragment_from_file.ng_level == 1
    assert len(fragment_from_file.section_contents) == 2

    """
    Fragment element #1: Section
    """
    fragment_section = fragment_from_file.section_contents[0]
    assert isinstance(fragment_section, SDocSection)
    assert fragment_section.ng_level == 1
    assert len(fragment_section.section_contents) == 2

    fragment_section_requirement = fragment_section.section_contents[0]
    assert isinstance(fragment_section_requirement, SDocNode)
    assert fragment_section_requirement.ng_level == 2

    """
    Fragment element #2: Requirement
    """
    fragment_requirement = fragment_from_file.section_contents[1]
    assert isinstance(fragment_requirement, SDocNode)
    assert fragment_requirement.ng_level == 1

    writer = SDWriter()
    document_output, fragments_output_dict = writer.write_with_fragments(
        document
    )

    assert document_content == document_output

    fragment_content_output = fragments_output_dict["test_fragment.ssec"]
    assert fragment_content == fragment_content_output


def test_002_nested_fragment(fake_filesystem):
    nested_fragment_content = """\
[FRAGMENT]

[SECTION]
TITLE: Nested section

[/SECTION]

[REQUIREMENT]
TITLE: Nested requirement

[COMPOSITE_REQUIREMENT]
TITLE: Nested composite requirement

[/COMPOSITE_REQUIREMENT]
"""

    fake_filesystem.create_file(
        "nested_fragment.ssec",
        contents=nested_fragment_content,
    )

    fragment_content = """\
[FRAGMENT]

[FRAGMENT_FROM_FILE]
FILE: nested_fragment.ssec
"""

    fake_filesystem.create_file(
        "fragment.ssec",
        contents=fragment_content,
    )

    """
    Main document fixture.
    """

    document_content = """\
[DOCUMENT]
TITLE: Test Doc

[FRAGMENT_FROM_FILE]
FILE: fragment.ssec
"""

    fake_filesystem.create_file("input.sdoc", contents=document_content)

    reader = SDReader()

    document = reader.read_from_file("input.sdoc")

    assert isinstance(document, SDocDocument)

    fragment_from_file: FragmentFromFile = document.section_contents[0]
    assert isinstance(fragment_from_file, FragmentFromFile)

    assert fragment_from_file.ng_level == 1
    assert len(fragment_from_file.section_contents) == 1

    nested_fragment_from_file: FragmentFromFile = (
        fragment_from_file.section_contents[0]
    )
    assert isinstance(nested_fragment_from_file, FragmentFromFile)

    assert nested_fragment_from_file.ng_level == 1
    assert len(nested_fragment_from_file.section_contents) == 3

    nested_fragment_section: SDocSection = (
        nested_fragment_from_file.section_contents[0]
    )
    assert isinstance(nested_fragment_section, SDocSection)
    assert nested_fragment_section.ng_level == 1

    nested_fragment_requirement: SDocNode = (
        nested_fragment_from_file.section_contents[1]
    )
    assert isinstance(nested_fragment_requirement, SDocNode)
    assert nested_fragment_requirement.ng_level == 1

    nested_fragment_composite_requirement: CompositeRequirement = (
        nested_fragment_from_file.section_contents[2]
    )
    assert isinstance(nested_fragment_composite_requirement, SDocNode)
    assert nested_fragment_composite_requirement.ng_level == 1

    writer = SDWriter()
    document_output, fragments_output_dict = writer.write_with_fragments(
        document
    )

    assert document_content == document_output

    fragment_content_output = fragments_output_dict["fragment.ssec"]
    assert fragment_content == fragment_content_output

    nested_fragment_content_output = fragments_output_dict[
        "nested_fragment.ssec"
    ]
    assert nested_fragment_content == nested_fragment_content_output
