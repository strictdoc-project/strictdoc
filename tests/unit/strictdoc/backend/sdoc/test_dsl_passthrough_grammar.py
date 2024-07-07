from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


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
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
SINGLE_CHOICE_FIELD: A
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
  - TITLE: SINGLE_CHOICE_FIELD
    TYPE: SingleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
SINGLE_CHOICE_FIELD: A
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert expected_sdoc == output


def test_152_grammar_multiple_choice(default_project_config):
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
  - TITLE: MULTIPLE_CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
MULTIPLE_CHOICE_FIELD: A, C
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
  - TITLE: MULTIPLE_CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
MULTIPLE_CHOICE_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert expected_sdoc == output


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
