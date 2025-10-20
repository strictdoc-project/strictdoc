"""
@relation(SDOC-SRS-136, scope=file)
"""

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.validations.sdoc_validator import SDocValidator
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.helpers.cast import assert_cast
from tests.unit.helpers.fake_document_meta import create_fake_document_meta


def test_150_grammar_minimal_doc(default_project_config):
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
""".lstrip()
    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert expected_sdoc == output


def test_151_grammar_single_choice(default_project_config):
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: SINGLE_CHOICE_FIELD
    TYPE: SingleChoice(A, B, C)
    REQUIRED: True
  - TITLE: SINGLE_CHOICE_FIELD_2
    TYPE: SingleChoice(Test/Hardware, Test/Software)
    REQUIRED: True
  - TITLE: SINGLE_CHOICE_FIELD_3
    TYPE: SingleChoice(Hardware test, Software test)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
SINGLE_CHOICE_FIELD: A
SINGLE_CHOICE_FIELD: Test/Hardware
SINGLE_CHOICE_FIELD: Hardware test
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_152_grammar_multiple_choice(default_project_config):
    input_sdoc = """\
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: MULTIPLE_CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True
  - TITLE: MULTIPLE_CHOICE_FIELD_2
    TYPE: MultipleChoice(Review, Test/Hardware)
    REQUIRED: True
  - TITLE: MULTIPLE_CHOICE_FIELD_3
    TYPE: MultipleChoice(Review of design, Hardware test)
    REQUIRED: True
  - TITLE: MULTIPLE_CHOICE_FIELD_4
    TYPE: MultipleChoice(review_of_design, hardware_test)
    REQUIRED: True
  - TITLE: MULTIPLE_CHOICE_FIELD_5
    TYPE: MultipleChoice(review-of-design, hardware-test)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
MULTIPLE_CHOICE_FIELD: A, C
MULTIPLE_CHOICE_FIELD_2: Review, Test/Hardware
MULTIPLE_CHOICE_FIELD_3: Review of design, Hardware test
MULTIPLE_CHOICE_FIELD_4: review_of_design, hardware_test
MULTIPLE_CHOICE_FIELD_5: review-of-design, hardware-test
"""

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document.meta = create_fake_document_meta()
    SDocValidator.validate_document(document)
    SDocValidator.validate_node(
        assert_cast(document.section_contents[0], SDocNode),
        document.grammar,
        "fake.path.sdoc",
        auto_uid_mode=False,
    )

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_153_grammar_tag(default_project_config):
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: TAG_FIELD
    TYPE: Tag
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
TAG_FIELD: A, C
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: TAG_FIELD
    TYPE: Tag
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
TAG_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert expected_sdoc == output


def test_154_grammar_multiline_custom_field(default_project_config):
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
  - TITLE: MY_FIELD
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
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
- TAG: TEXT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: MY_FIELD
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

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


def test_170_grammar_relations(default_project_config):
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent
  - TYPE: Parent
    ROLE: Refines
  - TYPE: Child
    ROLE: Refined_by

[LOW_LEVEL_REQUIREMENT]
STATEMENT: This is a statement.
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_180_additional_field_in_grammar():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Document

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: LEVEL
    TYPE: String
    REQUIRED: False
  - TITLE: STATUS
    TYPE: String
    REQUIRED: False
  - TITLE: TAGS
    TYPE: String
    REQUIRED: False
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  - TITLE: RATIONALE
    TYPE: String
    REQUIRED: False
  - TITLE: COMMENT
    TYPE: String
    REQUIRED: False
  - TITLE: META_TEST
    TYPE: String
    REQUIRED: False

[REQUIREMENT]
UID: A-1
STATEMENT: >>>
the foo must bar
<<<
COMMENT: >>>
Comment
<<<
META_TEST: >>>
Yes
<<<
    """.lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)

    requirement = document.section_contents[0]
    assert isinstance(requirement, SDocNode)
    # FIXME: More robust test.
    for _, value in requirement.enumerate_meta_fields():
        assert value.get_text_value() is not None


def test_190_element_properties(default_project_config):
    input_sdoc = """\
[DOCUMENT]
TITLE: Test Document

[GRAMMAR]
ELEMENTS:
- TAG: SECTION
  PROPERTIES:
    IS_COMPOSITE: True
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
- TAG: TEXT
  PROPERTIES:
    IS_COMPOSITE: False
    VIEW_STYLE: Plain
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
- TAG: REQUIREMENT
  PROPERTIES:
    IS_COMPOSITE: True
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  - TITLE: RATIONALE
    TYPE: String
    REQUIRED: False
  - TITLE: COMMENT
    TYPE: String
    REQUIRED: False

[[REQUIREMENT]]
UID: A-1
STATEMENT: >>>
the foo must bar
<<<

[[/REQUIREMENT]]
"""

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)
    assert input_sdoc == output
