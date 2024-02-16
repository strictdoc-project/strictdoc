from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.reference import BibReference
from strictdoc.backend.sdoc.models.type_system import (
    BibEntryFormat,
    ReferenceType,
)
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter

# FIXME: The SDReader class should accept a path parameter that can be used for
# calculating paths to referenced BibTex files.


def test_sdoc_bibliography_01():
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
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent

[BIBLIOGRAPHY]
BIBFILES:
- FORMAT: BibTex
  VALUE: tests/unit/strictdoc/backend/sdoc/bib-files/ctan_bibtex-test_test.bib
- FORMAT: BibTex
  VALUE: tests/unit/strictdoc/backend/sdoc/bib-files/ctan_biblatex-examples.bib
ENTRIES:
- FORMAT: String
  VALUE: RFC-0000, Testing only
- FORMAT: String
  VALUE: RFC-8446, "TLS Protocol Version 1.3", https://www.rfc-editor.org/rfc/rfc8446
- FORMAT: String
  VALUE: RFC-5246, "TLS Protocol Version 1.2", https://www.rfc-editor.org/rfc/rfc5246
- FORMAT: BibTex
  VALUE: @misc{CitekeyMisc, title="Pluto: The 'Other' Red Planet", author= "{NASA}", url="https://www.nasa.gov/nh/pluto-the-other-red-planet", year=2015, note="Accessed: 2022-12-23"}
""".lstrip()  # noqa: E501

    reader = SDReader()
    document = reader.read(sdoc_input)

    assert isinstance(document, SDocDocument)

    document_bibliography = document.bibliography
    assert len(document_bibliography.bib_files) == 2
    assert len(document_bibliography.bib_db.entries) == 181


def test_170_grammar_document_bibliography():
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
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  RELATIONS:
  - TYPE: Parent
  - TYPE: BibTex

[BIBLIOGRAPHY]
BIBFILES:
- FORMAT: BibTex
  VALUE: tests/unit/strictdoc/backend/sdoc/bib-files/ctan_bibtex-test_test.bib
- FORMAT: BibTex
  VALUE: tests/unit/strictdoc/backend/sdoc/bib-files/ctan_biblatex-examples.bib
ENTRIES:
- FORMAT: String
  VALUE: RFC-0000, Testing only
- FORMAT: String
  VALUE: RFC-8446, "TLS Protocol Version 1.3", https://www.rfc-editor.org/rfc/rfc8446
- FORMAT: String
  VALUE: RFC-5246, "TLS Protocol Version 1.2", https://www.rfc-editor.org/rfc/rfc5246
- FORMAT: BibTex
  VALUE: @misc{CitekeyMisc, title="Pluto: The 'Other' Red Planet", author= "{NASA}", url="https://www.nasa.gov/nh/pluto-the-other-red-planet", year=2015, note="Accessed: 2022-12-23"}

[LOW_LEVEL_REQUIREMENT]
UID: ID-001
RELATIONS:
- TYPE: BibTex
  FORMAT: BibTex
  VALUE: @book{hawking1989brief, title={A Brief History of Time: From the Big Bang to Black Holes}, author={Hawking, Stephen}, isbn={9780553176988}, year={1989}, publisher={Bantam Books} }

[LOW_LEVEL_REQUIREMENT]
UID: ID-002
RELATIONS:
- TYPE: BibTex
  FORMAT: String
  VALUE: SampleCiteKeyStringRef-1, "The sample BibReference String-Format"
- TYPE: BibTex
  FORMAT: String
  VALUE: SampleCiteKeyStringRef-2
- TYPE: BibTex
  FORMAT: Citation
  VALUE: hawking1989brief, section 2.1
""".lstrip()  # noqa: E501

    reader = SDReader()
    document = reader.read(sdoc_input)

    assert isinstance(document, SDocDocument)

    doc_bib = document.bibliography
    assert len(doc_bib.bib_files) == 2
    assert len(doc_bib.bib_db.entries) == 181

    file_entry = doc_bib.bib_files[0]
    assert (
        file_entry.g_file_path
        == "tests/unit/strictdoc/backend/sdoc/bib-files/ctan_bibtex-test_test.bib"
    )
    file_entry = doc_bib.bib_files[1]
    assert (
        file_entry.g_file_path
        == "tests/unit/strictdoc/backend/sdoc/bib-files/ctan_biblatex-examples.bib"
    )

    assert len(doc_bib.bib_entries) == 4

    ll_requirement = document.section_contents[1]
    references = ll_requirement.references
    assert len(references) == 3

    reference = references[0]
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

    reference = references[1]
    assert isinstance(reference, BibReference)
    assert reference.ref_type == ReferenceType.BIB_REF
    assert reference.bib_entry.bib_format == BibEntryFormat.STRING
    assert reference.bib_entry.bib_value == "SampleCiteKeyStringRef-2"
    assert reference.bib_entry.ref_cite == "SampleCiteKeyStringRef-2"
    assert reference.bib_entry.ref_detail is None
    assert reference.bib_entry.bibtex_entry is None

    reference = references[2]
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
