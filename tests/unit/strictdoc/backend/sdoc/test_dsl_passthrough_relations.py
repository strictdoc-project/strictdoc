"""
@relation(SDOC-SRS-136, scope=file)
"""

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_001_parent_relation_without_role(default_project_config):
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
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent

[REQUIREMENT]
STATEMENT: >>>
This is a statement.
<<<
RELATIONS:
- TYPE: Parent
  VALUE: ID-001
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output


def test_002_parent_relation_with_refines_role(default_project_config):
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
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent
    ROLE: Refines

[REQUIREMENT]
STATEMENT: >>>
This is a statement.
<<<
RELATIONS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output
