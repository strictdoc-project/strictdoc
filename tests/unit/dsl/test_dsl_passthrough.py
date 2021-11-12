from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import (
    Requirement,
    CompositeRequirement,
)
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.backend.dsl.writer import SDWriter


def test_001_minimal_doc():
    input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]

[REQUIREMENT]

[REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_010_multiple_sections():
    input = """
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

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


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
    input = """
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

    document = reader.read(input)
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

    assert input == output


def test_032_multiline_body():
    input = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[REQUIREMENT]
STATEMENT: Some statement
BODY: >>>
This is a body part 1
This is a body part 2
This is a body part 3
<<<

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output

    assert isinstance(
        document.section_contents[0].section_contents[0], Requirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert (
        requirement_1.body
        == "This is a body part 1\nThis is a body part 2\nThis is a body part 3"
    )


def test_036_rationale_singleline():
    input = """
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

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output

    assert isinstance(
        document.section_contents[0].section_contents[0], Requirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.rationale == "This is a Rationale"


def test_037_rationale_multiline():
    input = """
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

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output

    assert isinstance(
        document.section_contents[0].section_contents[0], Requirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert (
        requirement_1.rationale_multiline
        == "This is a Rationale line 1\nThis is a Rationale line 2\nThis is a Rationale line 3"
    )


def test_040_composite_requirement_1_level():
    input = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[COMPOSITE_REQUIREMENT]
STATEMENT: Some parent requirement statement
BODY: >>>
This is a body part 1
This is a body part 2
This is a body part 3
<<<

[REQUIREMENT]
STATEMENT: Some child requirement statement
BODY: >>>
This is a child body part 1
This is a child body part 2
This is a child body part 3
<<<

[/COMPOSITE_REQUIREMENT]

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output

    assert isinstance(
        document.section_contents[0].section_contents[0], CompositeRequirement
    )
    requirement_1 = document.section_contents[0].section_contents[0]
    assert requirement_1.ng_level == 2
    assert (
        requirement_1.body
        == "This is a body part 1\nThis is a body part 2\nThis is a body part 3"
    )


def test_042_composite_requirement_2_level():
    input = """
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[COMPOSITE_REQUIREMENT]
STATEMENT: 1.1 composite req statement
BODY: >>>
body composite 1.1
<<<

[COMPOSITE_REQUIREMENT]
STATEMENT: 1.1.1 composite req statement
BODY: >>>
body composite 1.1.1
<<<

[REQUIREMENT]
STATEMENT: 1.1.1.1 composite req statement
BODY: >>>
body 1.1.1.1
<<<

[/COMPOSITE_REQUIREMENT]

[/COMPOSITE_REQUIREMENT]

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output

    assert isinstance(
        document.section_contents[0].section_contents[0], CompositeRequirement
    )
    requirement_1_1 = document.section_contents[0].section_contents[0]
    assert requirement_1_1.ng_level == 2
    assert requirement_1_1.body == "body composite 1.1"

    assert isinstance(
        document.section_contents[0].section_contents[0].requirements[0],
        CompositeRequirement,
    )
    requirement_1_1_1 = (
        document.section_contents[0].section_contents[0].requirements[0]
    )
    assert requirement_1_1_1.ng_level == 3
    assert requirement_1_1_1.body == "body composite 1.1.1"

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
    assert requirement_1_1_1.body == "body 1.1.1.1"


def test_045_composite_requirement_custom_fields():
    input = """
[DOCUMENT]
TITLE: Test Doc
SPECIAL_FIELDS:
- NAME: ECSS_VERIFICATION
  TYPE: String

[COMPOSITE_REQUIREMENT]
SPECIAL_FIELDS:
  ECSS_VERIFICATION: R,A,I,T
STATEMENT: Some parent requirement statement

[REQUIREMENT]
STATEMENT: Some child requirement statement

[/COMPOSITE_REQUIREMENT]
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input == output

    assert isinstance(document.section_contents[0], CompositeRequirement)
    composite_req = document.section_contents[0]
    assert composite_req.ng_level == 1
    assert composite_req.special_fields[0].field_name == "ECSS_VERIFICATION"
    assert composite_req.special_fields[0].field_value == "R,A,I,T"


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
    input = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
    requirement = document.section_contents[0]
    assert len(requirement.references) == 1
    assert requirement.references[0].ref_type == "File"
    assert requirement.references[0].path == "/tmp/sample.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


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
NUMBER: SDOC-01

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    document: Document = reader.read(input)
    assert document.config.number == "SDOC-01"

    writer = SDWriter()
    output = writer.write(document)

    assert input == output


def test_100_basic_test():
    input = """
[DOCUMENT]
TITLE: Test Doc
SPECIAL_FIELDS:
- NAME: ECSS_VERIFICATION
  TYPE: String

[SECTION]
TITLE: Test Section

[REQUIREMENT]
TAGS: Tag 1, Tag 2, Tag 3
SPECIAL_FIELDS:
  ECSS_VERIFICATION: R,A,I,T
REFS:
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
STATEMENT: System shall do X
BODY: >>>
This is an optional body of the requirement.
This is an optional body of the requirement.
<<<
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

    document = reader.read(input)
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

    assert input == output


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
