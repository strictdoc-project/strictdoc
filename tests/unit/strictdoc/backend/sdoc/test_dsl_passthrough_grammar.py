import re

import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.reference import (
    BibReference,
    FileReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.type_system import (
    BibEntryFormat,
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
""".lstrip()
    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

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

[LOW_LEVEL_REQUIREMENT]
SINGLE_CHOICE_FIELD: A
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

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

[LOW_LEVEL_REQUIREMENT]
MULTIPLE_CHOICE_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

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

[LOW_LEVEL_REQUIREMENT]
TAG_FIELD: A, C
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

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

[REQUIREMENT]
MY_FIELD: >>>
Some text here...
Some text here...
Some text here...
<<<
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

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
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
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
  - TYPE: Bibtex

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

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

    ll_requirement = document.section_contents[2]
    references = ll_requirement.references
    assert len(references) == 4

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

    reference = references[3]
    assert reference.ref_type == ReferenceType.BIB_REF
    assert isinstance(reference, BibReference)
    assert (
        reference.bib_entry.bib_value == "SampleCiteKeyStringRef-1, "
        '"The sample BibReference String-Format"'
    )

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
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
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
  - TYPE: Bibtex

[LOW_LEVEL_REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /tmp/sample.cpp
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, Document)

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
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
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
  - TYPE: Bibtex

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
    assert isinstance(document, Document)

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


def test_163_grammar_refs_file_only():
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
    TYPE: Reference(FileReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
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
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocSemanticError
    assert re.fullmatch(
        "Requirement field of type Reference has an unsupported Reference "
        'Type item: ParentReqReference\\(.*ref_uid = "ID-001".*\\).',
        exc_info.value.args[0],
    )


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
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
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
  - TYPE: Bibtex

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
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
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
  - TYPE: Bibtex

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

    assert expected_sdoc == output


def test_166_grammar_refs_parent_only():
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
    TYPE: Reference(ParentReqReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
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
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocSemanticError

    assert re.fullmatch(
        "Requirement field of type Reference has an unsupported Reference"
        " Type item: FileReference\\(.*\\).",
        exc_info.value.args[0],
    )


def test_167_grammar_refs_bib():
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
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
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
  - TYPE: Bibtex

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

    document = reader.read(input_sdoc)
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

    assert expected_sdoc == output


def test_168_grammar_refs_bib_multi():
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
    TYPE: Reference(ParentReqReference, FileReference, BibReference)
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
- TYPE: BibRef
  FORMAT: String
  VALUE: SampleCiteKeyStringRef-1, "The sample BibReference String-Format"
- TYPE: BibRef
  FORMAT: BibTex
  VALUE: @book{hawking1989brief, title={A Brief History of Time: From the Big Bang to Black Holes}, author={Hawking, Stephen}, isbn={9780553176988}, year={1989}, publisher={Bantam Books} }
""".lstrip()  # noqa: E501

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
  - TYPE: Bibtex

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

    document = reader.read(input_sdoc)
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

    assert expected_sdoc == output


def test_169_grammar_refs_bib_only():
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
    TYPE: Reference(BibReference)
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
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
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocSemanticError

    assert re.fullmatch(
        "Requirement field of type Reference has an unsupported Reference "
        'Type item: ParentReqReference\\(.*ref_uid = "ID-001".*\\).',
        exc_info.value.args[0],
    )


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
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output
