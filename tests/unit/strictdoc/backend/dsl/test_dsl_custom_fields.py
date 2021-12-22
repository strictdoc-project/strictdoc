import pytest
import textx

from strictdoc.backend.dsl.error_handling import StrictDocSemanticError
from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.reader import SDReader


def test_001_custom_fields():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
SPECIAL_FIELDS:
- NAME: OWNER
  TYPE: String
- NAME: PRIORITY
  TYPE: String

[REQUIREMENT]
SPECIAL_FIELDS:
  OWNER: Person #1
  PRIORITY: 1
TITLE: Requirement 1
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    requirement = document.section_contents[0]

    assert requirement.special_fields[0].field_name == "OWNER"
    assert requirement.special_fields[0].field_value == "Person #1"
    assert requirement.special_fields[1].field_name == "PRIORITY"
    assert requirement.special_fields[1].field_value == "1"


def test_002_no_special_fields_declared():
    input = """
[DOCUMENT]
TITLE: Hello world doc

[REQUIREMENT]
SPECIAL_FIELDS:
  ECSS_COMPLIANCE: Compliant
""".lstrip()

    reader = SDReader()

    with pytest.raises(
        StrictDocSemanticError,
        match="Requirements special fields are not registered document-wide.",
    ) as _:
        reader.read(input)


def test_003_required_custom_field_missing():
    input = """
[DOCUMENT]
TITLE: Test Doc
SPECIAL_FIELDS:
- NAME: OWNER
  TYPE: String
- NAME: PRIORITY
  TYPE: String
  REQUIRED: Yes

[REQUIREMENT]
SPECIAL_FIELDS:
  OWNER: Person #1
TITLE: Requirement 1
""".lstrip()

    reader = SDReader()

    with pytest.raises(
        StrictDocSemanticError,
        match="Requirement is missing a required special field: PRIORITY.",
    ) as _:
        reader.read(input)


def test_004_custom_field_undeclared():
    input = """
[DOCUMENT]
TITLE: Test Doc
SPECIAL_FIELDS:
- NAME: PRIORITY
  TYPE: String

[REQUIREMENT]
SPECIAL_FIELDS:
  OWNER: Person #1
TITLE: Requirement 1
""".lstrip()

    reader = SDReader()

    with pytest.raises(
        StrictDocSemanticError, match="Undeclared special field: OWNER."
    ) as _:
        reader.read(input)
