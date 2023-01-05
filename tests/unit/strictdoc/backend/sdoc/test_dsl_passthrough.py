import re

import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.reference import (
    FileReference,
    ParentReqReference,
    BibReference,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    CompositeRequirement,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.models.type_system import (
    ReferenceType,
    BibEntryFormat,
)
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_001_minimal_doc():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]

[REQUIREMENT]

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_002_minimal_req():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TITLE: Hello
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_003_comments_01_several_comments():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TITLE: Hello
COMMENT: Comment #1
COMMENT: Comment #2
COMMENT: Comment #3
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_003_comments_02_single_line_empty():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
COMMENT:
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_003_comments_03_single_line_empty_and_space():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
COMMENT: 
""".lstrip()  # noqa: W291

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_003_comments_04_multiline_empty():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
COMMENT: >>>
<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_003_comments_05_multiline_empty_with_one_newline():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
COMMENT: >>>

<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_004_several_tags():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TAGS: A, B, C, D
TITLE: Hello
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


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


def test_020_free_text():
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


def test_021_freetext_empty():
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


def test_022_free_text_inline_link():
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


def test_023_free_text_():
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
        requirement_1.statement_multiline
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
    assert requirement_1.rationale_multiline == (
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
        requirement_1.comments[0].comment_multiline
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
    assert requirement_1_1.comments[0].comment_multiline == "body composite 1.1"

    assert isinstance(
        document.section_contents[0].section_contents[0].requirements[0],
        CompositeRequirement,
    )
    requirement_1_1_1 = (
        document.section_contents[0].section_contents[0].requirements[0]
    )
    assert requirement_1_1_1.ng_level == 3
    assert (
        requirement_1_1_1.comments[0].comment_multiline
        == "body composite 1.1.1"
    )

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
    assert requirement_1_1_1.comments[0].comment_multiline == "body 1.1.1.1"


# This test is needed to make sure that the grammar details related
# to the difference of parting single vs multiline strings are covered.
def test_050_requirement_single_line_statement_one_symbol():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: 1
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    document: Document = reader.read(sdoc_input)
    requirement = document.section_contents[0]
    assert requirement.statement == "1"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


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

    reference = references[0]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.file_entry.file_path == "/tmp/sample.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_070_document_config_version():
    input = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
    assert document.config.version == "0.0.1"

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_071_document_config_number():
    input = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
    assert document.config.uid == "SDOC-01"

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_072_document_config_classification():
    input = """
[DOCUMENT]
TITLE: Test Doc
UID: SDOC-01
VERSION: 0.0.1
CLASSIFICATION: Restricted

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
    assert document.config.classification == "Restricted"

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_090_document_config_all_fields():
    input = """
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

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
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
    assert section.level == "123"

    requirement = section.section_contents[0]
    assert isinstance(requirement, Requirement)
    assert requirement.level == "456"

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_100_basic_test():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[REQUIREMENT]
TAGS: Tag 1, Tag 2, Tag 3
REFS:
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
STATEMENT: System shall do X
COMMENT: This requirement is very important

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
    assert requirement_1.tags[0] == "Tag 1"
    assert requirement_1.tags[1] == "Tag 2"
    assert requirement_1.tags[2] == "Tag 3"

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_081_document_config_markup_not_specified():
    input = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
    assert document.config.version == "0.0.1"
    assert document.config.markup is None

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_081_document_config_markup_specified():
    input = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  MARKUP: Text

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
    assert document.config.version == "0.0.1"

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_082_document_config_auto_levels_specified_to_false():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  AUTO_LEVELS: Off
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    document: Document = reader.read(sdoc_input)
    assert document.config.auto_levels is False

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_083_requirement_level():
    sdoc_input = """
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

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    document: Document = reader.read(sdoc_input)
    assert document.config.auto_levels is False
    section = document.section_contents[0]
    assert section.level == "123"

    requirement = section.section_contents[0]
    assert isinstance(requirement, Requirement)
    assert requirement.level == "456"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_085_options_requirement_style():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  REQUIREMENT_STYLE: Table
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    document: Document = reader.read(sdoc_input)
    assert document.config.requirement_style == "Table"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_087_options_requirement_in_toc():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc
VERSION: 0.0.1
OPTIONS:
  REQUIREMENT_IN_TOC: True
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    document: Document = reader.read(sdoc_input)
    assert document.config.requirement_in_toc == "True"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_150_grammar_minimal_doc():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: CUSTOM_FIELD
    TYPE: String
    REQUIRED: True
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_151_grammar_single_choice():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: SINGLE_CHOICE_FIELD
    TYPE: SingleChoice(A, B, C)
    REQUIRED: True

[LOW_LEVEL_REQUIREMENT]
SINGLE_CHOICE_FIELD: A
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_152_grammar_multiple_choice():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: MULTIPLE_CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True

[LOW_LEVEL_REQUIREMENT]
MULTIPLE_CHOICE_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_153_grammar_tag():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: TAG_FIELD
    TYPE: Tag
    REQUIRED: True

[LOW_LEVEL_REQUIREMENT]
TAG_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_154_grammar_multiline_custom_field():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: MY_FIELD
    TYPE: String
    REQUIRED: True

[REQUIREMENT]
MY_FIELD: >>>
Some text here...
Some text here...
Some text here...
<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_160_grammar_refs():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-000

[LOW_LEVEL_REQUIREMENT]
UID: ID-001
REFS:
- TYPE: File
  VALUE: /tmp/sample0.cpp
- TYPE: Parent
  VALUE: ID-000
- TYPE: BibRef
  FORMAT: BibTex
  VALUE: @book{hawking1989brief, title={A Brief History of Time: From the Big Bang to Black Holes}, author={Hawking, Stephen}, isbn={9780553176988}, year={1989}, publisher={Bantam Books} }

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
- TYPE: File
  VALUE: /tmp/sample1.cpp
- TYPE: File
  VALUE: /tmp/sample2.cpp
- TYPE: BibRef
  FORMAT: String
  VALUE: SampleCiteKeyStringRef-1, "The sample BibReference String-Format"
""".lstrip()  # noqa: E501

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 4

    reference = references[0]
    assert isinstance(reference, ParentReqReference)
    assert reference.ref_type == ReferenceType.PARENT
    assert reference.ref_uid == "ID-001"

    reference = references[1]
    assert reference.ref_type == ReferenceType.FILE
    assert isinstance(reference, FileReference)
    assert reference.file_entry.file_path == "/tmp/sample1.cpp"

    reference = references[2]
    assert reference.ref_type == ReferenceType.FILE
    assert isinstance(reference, FileReference)
    assert reference.file_entry.file_path == "/tmp/sample2.cpp"

    reference = references[3]
    assert reference.ref_type == ReferenceType.BIB_REF
    assert isinstance(reference, BibReference)
    assert (
        reference.bib_entry.bib_value == "SampleCiteKeyStringRef-1, "
        '"The sample BibReference String-Format"'
    )

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_161_grammar_refs_file():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[0]
    references = ll_requirement.references
    assert len(references) == 1

    reference = references[0]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.file_entry.file_path == "/tmp/sample.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_162_grammar_refs_file_multi():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample1.cpp
- TYPE: File
  VALUE: /tmp/sample2.cpp
- TYPE: File
  VALUE: /tmp/sample3.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[0]
    references = ll_requirement.references
    assert len(references) == 3

    reference = references[0]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.file_entry.file_path == "/tmp/sample1.cpp"

    reference = references[1]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.file_entry.file_path == "/tmp/sample2.cpp"

    reference = references[2]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.file_entry.file_path == "/tmp/sample3.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_163_grammar_refs_file_only():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(FileReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
- TYPE: File
  VALUE: /tmp/sample1.cpp
""".lstrip()

    reader = SDReader()
    with pytest.raises(Exception) as exc_info:
        _ = reader.read(sdoc_input)

    assert exc_info.type is StrictDocSemanticError
    assert re.fullmatch(
        "Requirement field of type Reference has an unsupported Reference "
        'Type item: ParentReqReference\\(.*ref_uid = "ID-001".*\\)',
        exc_info.value.args[0],
    )


def test_164_grammar_refs_parent():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-000

[LOW_LEVEL_REQUIREMENT]
UID: ID-001
REFS:
- TYPE: File
  VALUE: /tmp/sample0.cpp
- TYPE: Parent
  VALUE: ID-000

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 1

    reference = references[0]
    assert isinstance(reference, ParentReqReference)
    assert reference.ref_type == ReferenceType.PARENT
    assert reference.ref_uid == "ID-001"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_165_grammar_refs_parent_multi():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-000

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-000
- TYPE: Parent
  VALUE: ID-001
""".lstrip()

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 2

    reference = references[0]
    assert isinstance(reference, ParentReqReference)
    assert reference.ref_type == ReferenceType.PARENT
    assert reference.ref_uid == "ID-000"

    reference = references[1]
    assert isinstance(reference, ParentReqReference)
    assert reference.ref_type == ReferenceType.PARENT
    assert reference.ref_uid == "ID-001"

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_166_grammar_refs_parent_only():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
- TYPE: File
  VALUE: /tmp/sample1.cpp
""".lstrip()

    reader = SDReader()
    with pytest.raises(Exception) as exc_info:
        _ = reader.read(sdoc_input)

    assert exc_info.type is StrictDocSemanticError

    assert re.fullmatch(
        "Requirement field of type Reference has an unsupported Reference"
        " Type item: FileReference\\(.*\\)",
        exc_info.value.args[0],
    )


def test_167_grammar_refs_bib():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-000

[LOW_LEVEL_REQUIREMENT]
UID: ID-001
REFS:
- TYPE: File
  VALUE: /tmp/sample0.cpp
- TYPE: Parent
  VALUE: ID-000
- TYPE: BibRef
  FORMAT: BibTex
  VALUE: @book{hawking1989brief, title={A Brief History of Time: From the Big Bang to Black Holes}, author={Hawking, Stephen}, isbn={9780553176988}, year={1989}, publisher={Bantam Books} }

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
- TYPE: BibRef
  FORMAT: String
  VALUE: SampleCiteKeyStringRef-1, "The sample BibReference String-Format"
- TYPE: BibRef
  FORMAT: String
  VALUE: SampleCiteKeyStringRef-2
- TYPE: BibRef
  FORMAT: Citation
  VALUE: hawking1989brief, section 2.1
""".lstrip()  # noqa: E501

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 4

    reference = references[1]
    assert isinstance(reference, BibReference)
    assert reference.ref_type == ReferenceType.BIB_REF
    assert reference.bib_entry.bib_format == BibEntryFormat.STRING
    assert (
        reference.bib_entry.bib_value == "SampleCiteKeyStringRef-1,"
        ' "The sample BibReference'
        ' String-Format"'
    )
    assert reference.bib_entry.ref_cite == "SampleCiteKeyStringRef-1"
    assert (
        reference.bib_entry.ref_detail
        == '"The sample BibReference String-Format"'
    )
    assert reference.bib_entry.bibtex_entry.type == "misc"
    assert (
        reference.bib_entry.bibtex_entry.fields["note"]
        == '"The sample BibReference String-Format"'
    )

    reference = references[2]
    assert isinstance(reference, BibReference)
    assert reference.ref_type == ReferenceType.BIB_REF
    assert reference.bib_entry.bib_format == BibEntryFormat.STRING
    assert reference.bib_entry.bib_value == "SampleCiteKeyStringRef-2"
    assert reference.bib_entry.ref_cite == "SampleCiteKeyStringRef-2"
    assert reference.bib_entry.ref_detail is None
    assert reference.bib_entry.bibtex_entry is None

    reference = references[3]
    assert isinstance(reference, BibReference)
    assert reference.ref_type == ReferenceType.BIB_REF
    assert reference.bib_entry.bib_format == BibEntryFormat.CITATION
    assert reference.bib_entry.bib_value == "hawking1989brief, section 2.1"
    assert reference.bib_entry.ref_cite == "hawking1989brief"
    assert reference.bib_entry.ref_detail == "section 2.1"
    assert reference.bib_entry.bibtex_entry is None

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_168_grammar_refs_bib_multi():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-000

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: BibRef
  FORMAT: String
  VALUE: SampleCiteKeyStringRef-1, "The sample BibReference String-Format"
- TYPE: BibRef
  FORMAT: BibTex
  VALUE: @book{hawking1989brief, title={A Brief History of Time: From the Big Bang to Black Holes}, author={Hawking, Stephen}, isbn={9780553176988}, year={1989}, publisher={Bantam Books} }
""".lstrip()  # noqa: E501

    reader = SDReader()

    document = reader.read(sdoc_input)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 2

    reference = references[0]
    assert isinstance(reference, BibReference)
    assert reference.ref_type == ReferenceType.BIB_REF
    assert (
        reference.bib_entry.bib_value == "SampleCiteKeyStringRef-1, "
        '"The sample BibReference String-Format"'
    )

    reference = references[1]
    assert isinstance(reference, BibReference)
    assert reference.ref_type == ReferenceType.BIB_REF
    assert reference.bib_entry.bib_value == (
        "@book{hawking1989brief, "
        "title={A Brief History of Time: From the Big Bang to Black Holes}, "
        "author={Hawking, Stephen}, "
        "isbn={9780553176988}, "
        "year={1989}, "
        "publisher={Bantam Books} "
        "}"
    )  # noqa: E501

    writer = SDWriter()
    output = writer.write(document)

    assert sdoc_input == output


def test_169_grammar_refs_bib_only():
    sdoc_input = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: REFS
    TYPE: Reference(BibReference)
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
UID: ID-001

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
REFS:
- TYPE: Parent
  VALUE: ID-001
- TYPE: BibRef
  FORMAT: BibTex
  VALUE: @book{hawking1989brief, title={A Brief History of Time: From the Big Bang to Black Holes}, author={Hawking, Stephen}, isbn={9780553176988}, year={1989}, publisher={Bantam Books} }
""".lstrip()  # noqa: E501

    reader = SDReader()
    with pytest.raises(Exception) as exc_info:
        _ = reader.read(sdoc_input)

    assert exc_info.type is StrictDocSemanticError

    assert re.fullmatch(
        "Requirement field of type Reference has an unsupported Reference "
        'Type item: ParentReqReference\\(.*ref_uid = "ID-001".*\\)',
        exc_info.value.args[0],
    )
