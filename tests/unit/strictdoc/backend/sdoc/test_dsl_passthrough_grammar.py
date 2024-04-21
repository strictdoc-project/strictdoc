from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.reference import (
    FileReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.type_system import (
    ReferenceType,
)
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_150_grammar_minimal_doc():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent
  - TYPE: File
""".lstrip()
    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_151_grammar_single_choice():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: SINGLE_CHOICE_FIELD
    TYPE: SingleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

[LOW_LEVEL_REQUIREMENT]
SINGLE_CHOICE_FIELD: A
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_152_grammar_multiple_choice():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: MULTIPLE_CHOICE_FIELD
    TYPE: MultipleChoice(A, B, C)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

[LOW_LEVEL_REQUIREMENT]
MULTIPLE_CHOICE_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_153_grammar_tag():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
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
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: TAG_FIELD
    TYPE: Tag
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

[LOW_LEVEL_REQUIREMENT]
TAG_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_154_grammar_multiline_custom_field():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
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
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: MY_FIELD
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

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

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_160_grammar_refs():
    input_sdoc = """
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
    TYPE: Reference(ParentReqReference, FileReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
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
- TYPE: File
  VALUE: /tmp/sample1.cpp
- TYPE: File
  VALUE: /tmp/sample2.cpp
""".lstrip()

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

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
- TYPE: File
  VALUE: /tmp/sample1.cpp
- TYPE: File
  VALUE: /tmp/sample2.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 3

    reference = references[0]
    assert isinstance(reference, ParentReqReference)
    assert reference.ref_type == ReferenceType.PARENT
    assert reference.ref_uid == "ID-001"

    reference: FileReference = references[1]
    assert reference.ref_type == ReferenceType.FILE
    assert isinstance(reference, FileReference)
    assert reference.g_file_entry.g_file_path == "/tmp/sample1.cpp"

    reference = references[2]
    assert reference.ref_type == ReferenceType.FILE
    assert isinstance(reference, FileReference)
    assert reference.g_file_entry.g_file_path == "/tmp/sample2.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_161_grammar_refs_file():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False

[LOW_LEVEL_REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

[LOW_LEVEL_REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    ll_requirement = document.section_contents[0]
    references = ll_requirement.references
    assert len(references) == 1

    reference: FileReference = references[0]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.g_file_entry.g_file_path == "/tmp/sample.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_162_grammar_refs_file_multi():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: REFS
    TYPE: Reference(ParentReqReference, FileReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
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

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

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

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    ll_requirement = document.section_contents[0]
    references = ll_requirement.references
    assert len(references) == 3

    reference: FileReference = references[0]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.g_file_entry.g_file_path == "/tmp/sample1.cpp"

    reference = references[1]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.g_file_entry.g_file_path == "/tmp/sample2.cpp"

    reference = references[2]
    assert isinstance(reference, FileReference)
    assert reference.ref_type == ReferenceType.FILE
    assert reference.g_file_entry.g_file_path == "/tmp/sample3.cpp"

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_164_grammar_refs_parent():
    input_sdoc = """
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
    TYPE: Reference(ParentReqReference, FileReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
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

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

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

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 1

    reference = references[0]
    assert isinstance(reference, ParentReqReference)
    assert reference.ref_type == ReferenceType.PARENT
    assert reference.ref_uid == "ID-001"

    writer = SDWriter()
    output = writer.write(document)

    assert expected_sdoc == output


def test_165_grammar_refs_parent_multi():
    input_sdoc = """
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
    TYPE: Reference(ParentReqReference, FileReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
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

    expected_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
- TAG: LOW_LEVEL_REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: File

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

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

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

    assert expected_sdoc == output


def test_170_grammar_refs():
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc

[GRAMMAR]
ELEMENTS:
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

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output
