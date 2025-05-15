from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_010_multiple_sections(default_project_config):
    input_sdoc = """\
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[SECTION]
TITLE: Test Section (Nested)

[SECTION]
TITLE: Test Section (Sub-nested)

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[/SECTION]

[/SECTION]

[/SECTION]
"""

    output_sdoc = """\
[DOCUMENT]
TITLE: Test Doc

[[SECTION]]
TITLE: Test Section

[[SECTION]]
TITLE: Test Section (Nested)

[[SECTION]]
TITLE: Test Section (Sub-nested)

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[[/SECTION]]

[[/SECTION]]

[[/SECTION]]
"""

    reader = SDReader()

    document = reader.read(input_sdoc, migrate_sections=True)
    assert isinstance(document, SDocDocument)

    writer = SDWriter(default_project_config)
    output = writer.write(document)
    assert output == output_sdoc
