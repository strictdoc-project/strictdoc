from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter


def test_01_integrated_example(default_project_config):
    input_sdoc = """
[DOCUMENT]
TITLE: Test Doc
OPTIONS:
  REQUIREMENT_STYLE: Inline
  DEFAULT_VIEW: PRINT_VIEW
VIEWS:
- ID: PRINT_VIEW
  NAME: Print view
  TAGS:
  - OBJECT_TYPE: REQUIREMENT
    VISIBLE_FIELDS:
    - NAME: UID
      PLACEMENT: XYZ
    - NAME: STATEMENT
    - NAME: RATIONALE
- ID: SECOND_VIEW
  TAGS:
  - OBJECT_TYPE: REQUIREMENT
    VISIBLE_FIELDS:
    - NAME: TITLE
      PLACEMENT: ABC
    - NAME: STATEMENT
    - NAME: RATIONALE
  HIDDEN_TAGS:
  - SECOND_OBJ
""".lstrip()

    reader = SDReader()

    document = reader.read(input_sdoc)
    assert isinstance(document, SDocDocument)

    document: SDocDocument = reader.read(input_sdoc)

    writer = SDWriter(default_project_config)
    output = writer.write(document)

    assert input_sdoc == output
