import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.reader import SDReader


def test_001_validate_unregistered_child_relation_type():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent

[REQUIREMENT]
UID: ID-002
STATEMENT: >>>
This is a statement.
<<<
REFS:
- TYPE: Child
  VALUE: ID-001
""".lstrip()

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: Child."
    )
    assert exception.hint == "Problematic requirement: ID-002."


def test_002_validate_unregistered_role():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
UID: REQ-001
STATEMENT: >>>
This is a statement.
<<<
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    exception: StrictDocSemanticError = exc_info.value
    assert exception.title == (
        "Requirement relation type/role is not registered: Parent / Refines."
    )
    assert exception.hint == "Problematic requirement: REQ-001."
