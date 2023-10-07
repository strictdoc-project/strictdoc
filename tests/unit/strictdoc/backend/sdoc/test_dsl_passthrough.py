import pytest
from textx import TextXSyntaxError

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.reference import (
    FileReference,
)
from strictdoc.backend.sdoc.models.requirement import (
    CompositeRequirement,
    Requirement,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.models.type_system import (
    ReferenceType,
)
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_001_minimal_doc():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]

[REQUIREMENT]

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_002_minimal_req():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TITLE: Hello
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_003_comments_01_several_comments():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TITLE: Hello
COMMENT: Comment #1
COMMENT: Comment #2
COMMENT: Comment #3
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_004_several_tags():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TAGS: A, B, C, D
TITLE: Hello
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_010_multiple_sections():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[/SECTION]

[SECTION]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_030_multiline_statement():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    assert isinstance(
        document.section_contents[0].section_contents[0], Requirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert (
        requirement_1.reserved_statement
        == "This is a statement 1\nThis is a statement 2\nThis is a statement 3"
    )

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_036_rationale_single_line():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: Some statement
RATIONALE: This is a Rationale

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output

    assert isinstance(
        document.section_contents[0].section_contents[0], Requirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.rationale == "This is a Rationale"


def test_037_rationale_multi_line():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: Some statement
RATIONALE: >>>
This is a Rationale line 1
This is a Rationale line 2
This is a Rationale line 3
<<<

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output

    assert isinstance(
        document.section_contents[0].section_contents[0], Requirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.rationale == (
        "This is a Rationale line 1\n"
        "This is a Rationale line 2\n"
        "This is a Rationale line 3"
    )


def test_040_composite_requirement_1_level():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[COMPOSITE_REQUIREMENT]
STATEMENT: Some parent requirement statement
COMMENT: >>>
This is a body part 1
This is a body part 2
This is a body part 3
<<<

[REQUIREMENT]
STATEMENT: Some child requirement statement
COMMENT: >>>
This is a child body part 1
This is a child body part 2
This is a child body part 3
<<<

[/COMPOSITE_REQUIREMENT]

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output

    assert isinstance(
        document.section_contents[0].section_contents[0], CompositeRequirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.ng_level == 2
    assert (
        requirement_1.comments[0]
        == "This is a body part 1\nThis is a body part 2\nThis is a body part 3"
    )


def test_042_composite_requirement_2_level():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[COMPOSITE_REQUIREMENT]
STATEMENT: 1.1 composite req statement
COMMENT: >>>
body composite 1.1
<<<

[COMPOSITE_REQUIREMENT]
STATEMENT: 1.1.1 composite req statement
COMMENT: >>>
body composite 1.1.1
<<<

[REQUIREMENT]
STATEMENT: 1.1.1.1 composite req statement
COMMENT: >>>
body 1.1.1.1
<<<

[/COMPOSITE_REQUIREMENT]

[/COMPOSITE_REQUIREMENT]

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output

    assert isinstance(
        document.section_contents[0].section_contents[0], CompositeRequirement
    )
    requirement_1_1 = document.section_contents[0].section_contents[0]
    assert requirement_1_1.ng_level == 2
    assert requirement_1_1.comments[0] == "body composite 1.1"

    assert isinstance(
        document.section_contents[0].section_contents[0].requirements[0],
        CompositeRequirement,
    )
    requirement_1_1_1 = (
        document.section_contents[0].section_contents[0].requirements[0]
    )
    assert requirement_1_1_1.ng_level == 3
    assert requirement_1_1_1.comments[0] == "body composite 1.1.1"

    assert isinstance(
        document.section_contents[0]
        .section_contents[0]
        .requirements[0]
        .requirements[0],
        Requirement,
    )
    requirement_1_1_1 = (
        document.section_contents[0]
        .section_contents[0]
        .requirements[0]
        .requirements[0]
    )
    assert requirement_1_1_1.ng_level == 4
    assert requirement_1_1_1.comments[0] == "body 1.1.1.1"


# This test is needed to make sure that the grammar details related
# to the difference of parting single vs multiline strings are covered.
def test_050_requirement_single_line_statement_one_symbol():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: 1
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    requirement = document.section_contents[0]
    assert requirement.reserved_statement == "1"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_060_file_ref():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    requirement = document.section_contents[0]
    references = requirement.references
    assert len(references) == 1

    reference: FileReference = references[0]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.g_file_entry.g_file_path == "/tmp/sample.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_070_document_config_version():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.version == "0.0.1"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_071_document_config_number():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.uid == "SDOC-01"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_072_document_config_classification():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
CLASSIFICATION: Restricted

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.classification == "Restricted"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_073_document_config_requirement_prefix():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
REQ_PREFIX: DOC-

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.requirement_prefix == "DOC-"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_090_document_config_all_fields():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
CLASSIFICATION: Restricted
OPTIONS:
  MARKUP: Text
  AUTO_LEVELS: Off
  REQUIREMENT_STYLE: Table
  REQUIREMENT_IN_TOC: True

[SECTION]
LEVEL: 123
TITLE: "Section"

[REQUIREMENT]
LEVEL: 456
STATEMENT: ABC

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.title == "Test Doc"
    assert document.config.version == "0.0.1"
    assert document.config.uid == "SDOC-01"
    assert document.config.classification == "Restricted"
    assert document.config.markup == "Text"
    assert document.config.auto_levels is False
    assert document.config.requirement_style == "Table"
    assert document.config.requirement_in_toc == "True"

    section = document.section_contents[0]
    assert isinstance(section, Section)
    assert section.custom_level == "123"

    requirement = section.section_contents[0]
    assert isinstance(requirement, Requirement)
    assert requirement.custom_level == "456"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_100_basic_test():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[REQUIREMENT]
TAGS: Tag 1, Tag 2, Tag 3
STATEMENT: System shall do X
COMMENT: This requirement is very important
REFS:
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe

[REQUIREMENT]
UID: REQ-001
STATUS: Draft
TITLE: Optional title B
STATEMENT: System shall do Y
COMMENT: This requirement is very important

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    assert isinstance(
        document.section_contents[0].section_contents[0], Requirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.reserved_tags[0] == "Tag 1"
    assert requirement_1.reserved_tags[1] == "Tag 2"
    assert requirement_1.reserved_tags[2] == "Tag 3"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_081_document_config_markup_not_specified():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.version == "0.0.1"
    assert document.config.markup is None

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_081_document_config_markup_specified():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  MARKUP: Text

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.version == "0.0.1"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_082_document_config_auto_levels_specified_to_false():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  AUTO_LEVELS: Off
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.auto_levels is False

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_083_requirement_level():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  AUTO_LEVELS: Off

[SECTION]
LEVEL: 123
TITLE: "Section"

[REQUIREMENT]
LEVEL: 456
STATEMENT: ABC

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.auto_levels is False
    section: Section = document.section_contents[0]
    assert section.custom_level == "123"

    requirement = section.section_contents[0]
    assert isinstance(requirement, Requirement)
    assert requirement.custom_level == "456"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_085_options_requirement_style():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  REQUIREMENT_STYLE: Table
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.requirement_style == "Table"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_087_options_requirement_in_toc():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  REQUIREMENT_IN_TOC: True
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    document: Document = reader.read(input_sdoc)
    assert document.config.requirement_in_toc == "True"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_edge_case_01_minimal_requirement():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document: Document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    requirement: Requirement = document.section_contents[0]
    assert requirement.reserved_uid is None
    assert requirement.reserved_title is None
    assert requirement.reserved_statement is None

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_edge_case_02_uid_present_but_empty_with_no_space_character():
    # Note: There is no whitespace character after "UID:".
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
UID:
""".lstrip()

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert "Expected ' '" == exc_info.value.args[0].decode("utf-8")


def test_edge_case_03_uid_present_but_empty_with_space_character():
    # Note: There is a whitespace character after "UID:".
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
UID: 
""".lstrip()  # noqa: W291

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert "Expected SingleLineString or '>>>\\n'" in exc_info.value.args[
        0
    ].decode("utf-8")


def test_edge_case_04_uid_present_but_empty_with_two_space_characters():
    # Note: There are two whitespace characters after "UID:".
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
UID:  
""".lstrip()  # noqa: W291

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert "Expected SingleLineString or '>>>\\n'" in exc_info.value.args[
        0
    ].decode("utf-8")


def test_edge_case_10_empty_multiline_field():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
COMMENT: >>>
<<<
""".lstrip()

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert (
        "Expected '(?ms)(?!^<<<) *(?!^<<<)\\S((?!^<<<).)+'"
        in exc_info.value.args[0].decode("utf-8")
    )


def test_edge_case_11_empty_multiline_field_with_one_newline():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
COMMENT: >>>

<<<
""".lstrip()

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert (
        "Expected '(?ms)(?!^<<<) *(?!^<<<)\\S((?!^<<<).)+'"
        in exc_info.value.args[0].decode("utf-8")
    )


def test_edge_case_20_empty_section_title():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE:

[/SECTION]
""".lstrip()

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert "Expected 'UID: ' or 'LEVEL: ' or 'TITLE: '" == exc_info.value.args[
        0
    ].decode("utf-8")


def test_edge_case_21_section_title_with_empty_space():
    # Empty space after TITLE:
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: 

[/SECTION]
""".lstrip()  # noqa: W291

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert "Expected SingleLineString" in exc_info.value.args[0].decode("utf-8")


def test_edge_case_22_section_title_with_two_empty_spaces():
    # Two empty spaces after TITLE:
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE:  

[/SECTION]
""".lstrip()  # noqa: W291

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is TextXSyntaxError
    assert "Expected SingleLineString" in exc_info.value.args[0].decode("utf-8")


def test_edge_case_23_leading_spaces_do_not_imply_empy_field():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  - TITLE: MY_FIELD
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference)
    REQUIRED: False

[REQUIREMENT]
MY_FIELD: >>>
    Some text here...
    Some text here...
    Some text here...
<<<
""".lstrip()

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  - TITLE: MY_FIELD
    TYPE: String
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent

[REQUIREMENT]
MY_FIELD: >>>
    Some text here...
    Some text here...
    Some text here...
<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)
    assert expected_sdoc == output
