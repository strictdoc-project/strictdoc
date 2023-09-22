from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_001_new_refs():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: >>>
This is a statement.
<<<
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_002_new_refs_moves_refs():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
STATEMENT: >>>
This is a statement.
<<<
""".lstrip()

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: >>>
This is a statement.
<<<
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_003_new_refs_moves_refs():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
STATEMENT: >>>
This is a statement.
<<<
COMMENT: >>>
This is a comment.
<<<
""".lstrip()

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: >>>
This is a statement.
<<<
COMMENT: >>>
This is a comment.
<<<
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_004_new_refs_moves_refs():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TITLE: This is a title.
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
STATEMENT: >>>
This is a statement.
<<<
COMMENT: >>>
This is a comment.
<<<
""".lstrip()

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
TITLE: This is a title.
STATEMENT: >>>
This is a statement.
<<<
COMMENT: >>>
This is a comment.
<<<
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_005_new_refs_with_correct_grammar():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
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
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output


def test_020_parent_ref_with_relation():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[REQUIREMENT]
STATEMENT: >>>
This is a statement.
<<<
REFS:
- TYPE: Parent
  VALUE: ID-001
  ROLE: Refines
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output
