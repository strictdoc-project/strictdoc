"""
@relation(SDOC-SRS-136, scope=file)
"""

import pytest

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.grammar_element import ReferenceType
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
)
from strictdoc.backend.sdoc.models.reference import (
    FileReference,
)
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.helpers.exception import StrictDocException


def test_001_minimal_doc(default_project_config):
    input_sdoc = """\
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: ...

[REQUIREMENT]
STATEMENT: ...

[REQUIREMENT]
STATEMENT: ...
"""

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_002_minimal_req(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TITLE: Hello
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_005_requirement_UID_supports_special_characters(
    default_project_config,
):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
UID: FOO-1
TITLE: Hello

[REQUIREMENT]
UID: FOO.1
TITLE: Hello

[REQUIREMENT]
UID: FOO/1
TITLE: Hello

[REQUIREMENT]
UID: FOO_1
TITLE: Hello

[REQUIREMENT]
UID: FOO 1
TITLE: Hello

[REQUIREMENT]
UID: FOO::1
TITLE: Hello
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_003_comments_01_several_comments(default_project_config):
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
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_004_several_tags(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TAGS: A, B, C, D
TITLE: Hello
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_010_multiple_sections(default_project_config):
    input_sdoc = """\
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[[/SECTION]]

[[SECTION]]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[[/SECTION]]
"""

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)
    assert input_sdoc == output


def test_020_requirement_mid(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: MID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
MID: abcdef123456
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)
    assert input_sdoc == output


def test_021_section_and_document_mid(default_project_config):
    input_sdoc = """
[DOCUMENT]
MID: xyz09876
TITLE: Test Doc
OPTIONS:
  ENABLE_MID: True

[[SECTION]]
MID: abcdef123456
TITLE: Test Section

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_022_requirement_uid_and_link(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
UID: With spaces and (_-.) and non latin 特点
STATEMENT: >>>
This is a statement.

[TEXT]
STATEMENT: >>>
[LINK: With spaces and (_-.) and non latin 特点]
<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_030_multiline_statement(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    assert isinstance(
        document.section_contents[0].section_contents[0], SDocNode
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert (
        requirement_1.reserved_statement
        == "This is a statement 1\nThis is a statement 2\nThis is a statement 3\n"
    )

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_036_rationale_single_line(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: Some statement
RATIONALE: This is a Rationale

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output

    assert isinstance(
        document.section_contents[0].section_contents[0], SDocNode
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.rationale == "This is a Rationale"


def test_037_rationale_multi_line(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: Some statement
RATIONALE: >>>
This is a Rationale line 1
This is a Rationale line 2
This is a Rationale line 3
<<<

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output

    assert isinstance(
        document.section_contents[0].section_contents[0], SDocNode
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.rationale == (
        "This is a Rationale line 1\n"
        "This is a Rationale line 2\n"
        "This is a Rationale line 3\n"
    )


# This test is needed to make sure that the grammar details related
# to the difference of parting single vs multiline strings are covered.
def test_050_requirement_single_line_statement_one_symbol(
    default_project_config,
):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: 1
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    requirement = document.section_contents[0]
    assert requirement.reserved_statement == "1"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_060_file_ref(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: ...
RELATIONS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    requirement: SDocNode = document.section_contents[0]
    relations = requirement.relations
    assert len(relations) == 1

    reference: FileReference = relations[0]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.g_file_entry.g_file_path == "/tmp/sample.cpp"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_070_document_config_version(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1

[REQUIREMENT]
STATEMENT: ...
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.version == "0.0.1"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_071_document_config_number(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01

[REQUIREMENT]
STATEMENT: ...
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.uid == "SDOC-01"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_072_document_config_classification(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
CLASSIFICATION: Restricted

[REQUIREMENT]
STATEMENT: ...
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.classification == "Restricted"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_073_document_config_requirement_prefix(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
PREFIX: DOC-

[REQUIREMENT]
STATEMENT: ...
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.requirement_prefix == "DOC-"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_074_document_config_metadata(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
METADATA:
  AUTHOR: James T. Kirk
  CHECKED-BY: Chuck Norris
  APPROVED-BY: Wile E. Coyote

[REQUIREMENT]
UID: FOO
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_090_document_config_all_fields(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
CLASSIFICATION: Restricted
ROOT: True
OPTIONS:
  MARKUP: Text
  AUTO_LEVELS: Off
  LAYOUT: Website
  VIEW_STYLE: Table
  NODE_IN_TOC: True

[[SECTION]]
LEVEL: 123
TITLE: "Section"

[REQUIREMENT]
LEVEL: 456
STATEMENT: ABC

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.title == "Test Doc"
    assert document.config.version == "0.0.1"
    assert document.config.uid == "SDOC-01"
    assert document.config.classification == "Restricted"
    assert document.config.root is True
    assert document.config.markup == "Text"
    assert document.config.auto_levels is False
    assert document.config.requirement_style == "Table"
    assert document.config.requirement_in_toc == "True"

    section = document.section_contents[0]
    assert isinstance(section, SDocNode)
    assert section.custom_level == "123"

    requirement = section.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.custom_level == "456"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_100_basic_test(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: Test Section

[REQUIREMENT]
TAGS: Tag 1, Tag 2, Tag 3
STATEMENT: System shall do X
COMMENT: This requirement is very important
RELATIONS:
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

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    assert isinstance(
        document.section_contents[0].section_contents[0], SDocNode
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.reserved_tags[0] == "Tag 1"
    assert requirement_1.reserved_tags[1] == "Tag 2"
    assert requirement_1.reserved_tags[2] == "Tag 3"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_081_document_config_markup_not_specified(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1

[REQUIREMENT]
TITLE: ...
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.version == "0.0.1"
    assert document.config.markup is None

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_081_document_config_markup_specified(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  MARKUP: Text

[REQUIREMENT]
STATEMENT: ...
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.version == "0.0.1"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_082_document_config_auto_levels_specified_to_false(
    default_project_config,
):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  AUTO_LEVELS: Off
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.auto_levels is False

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_083_requirement_level(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  AUTO_LEVELS: Off

[[SECTION]]
LEVEL: 123
TITLE: "Section"

[REQUIREMENT]
LEVEL: 456
STATEMENT: ABC

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.auto_levels is False
    section: SDocNode = document.section_contents[0]
    assert section.custom_level == "123"

    requirement = section.section_contents[0]
    assert isinstance(requirement, SDocNode)
    assert requirement.custom_level == "456"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_085_options_requirement_style(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  VIEW_STYLE: Table
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.requirement_style == "Table"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_087_options_requirement_in_toc(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  NODE_IN_TOC: True
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.requirement_in_toc == "True"

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_089_document_config_use_mid(default_project_config):
    input_sdoc = """
[DOCUMENT]
MID: foobar
TITLE: Test Doc
OPTIONS:
  ENABLE_MID: True
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)
    assert document.config.enable_mid is True

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_090_byte_order_mark_symbol_does_not_cause_parsing_errors():
    input_sdoc = (
        "\ufeff"
        """\
[DOCUMENT]
TITLE: Test Doc
"""
    )

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)


def test__validation__30__composite_node_start_end_tags_do_not_match():
    input_sdoc = """\
[DOCUMENT]
TITLE: Test Doc

[[REQUIREMENT]]
UID: TITLE

[[/FOOBAR]]
""".lstrip()

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocException
    assert exc_info.value.args[0] == (
        "[[NODE]] syntax error: "
        "Opening and closing tags must match: "
        "opening: REQUIREMENT, closing: FOOBAR."
    )


def test_edge_case_01_minimal_requirement(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: ...
""".lstrip()

    reader = SDReader()

    document: SDocDocument = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    requirement: SDocNode = document.section_contents[0]
    assert requirement.reserved_uid is None
    assert requirement.reserved_title is None
    assert requirement.reserved_statement == "..."

    writer = SDWriter(default_project_config)
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

    assert exc_info.type is StrictDocException
    assert "Expected ': '" in exc_info.value.args[0]


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

    assert exc_info.type is StrictDocException
    assert "Expected '([\\w]+[\\w()\\-\\/.: ]*)'" in exc_info.value.args[0]


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

    assert exc_info.type is StrictDocException
    assert "Expected '([\\w]+[\\w()\\-\\/.: ]*)'" in exc_info.value.args[0]


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

    assert exc_info.type is StrictDocException
    assert (
        "Expected '^\\[ANCHOR: ' or '[LINK: ' or "
        "'(?ms)(?!^<<<)(?!\\[LINK: "
        "([\\w]+[\\w()\\-\\/.: ]*))(?!^\\[ANCHOR: "
        "([\\w]+[\\w()\\-\\/.: ]*)).'" in exc_info.value.args[0]
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

    assert exc_info.type is StrictDocException
    assert "Node statement cannot be empty." in exc_info.value.args[0]


def test_edge_case_19_empty_section_title():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE:

[[/SECTION]]
""".lstrip()

    reader = SDReader()

    with pytest.raises(StrictDocException) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocException
    assert "TITLE:*" in exc_info.value.args[0]
    assert "Expected ' '" in exc_info.value.args[0]


def test_edge_case_20_empty_section_title():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: 

[[/SECTION]]
""".lstrip()  # noqa: W291

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocException
    assert "TITLE: *" in exc_info.value.args[0]


def test_edge_case_21_section_title_with_empty_space():
    # Empty space after TITLE:
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: 

[[/SECTION]]
""".lstrip()  # noqa: W291

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocException
    assert "TITLE: *" in exc_info.value.args[0]


def test_edge_case_22_section_title_with_two_empty_spaces():
    # Two empty spaces after TITLE:
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE:  

[[/SECTION]]
""".lstrip()  # noqa: W291

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocException
    assert "TITLE: *" in exc_info.value.args[0]


def test_edge_case_23_leading_spaces_do_not_imply_empy_field(
    default_project_config,
):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
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

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
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
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)
    assert expected_sdoc == output
