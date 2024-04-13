from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_001_minimal_doc():
    input_sdoc = """
[DOCUMENT]
TITLE: Fragment

[GRAMMAR]
IMPORT_FROM_FILE: grammar.sgra

[SECTION]
TITLE: First section

[/SECTION]
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    writer = SDWriter()
    output = writer.write(document)

    assert input_sdoc == output
