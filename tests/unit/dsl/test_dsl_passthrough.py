from strictdoc.backend.dsl.models import Document
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.backend.dsl.writer import SDWriter


def test_100_basic_test():
    input = """
[DOCUMENT]
NAME: Test Doc

[SECTION]
LEVEL: 0
TITLE: Test Section

[REQUIREMENT]
REFS:
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
- TYPE: File
  VALUE: /usr/local/bin/hexe
STATEMENT: System shall do X
BODY: >>>
This is an optional body of the requirement.
This is an optional body of the requirement.
<<<
COMMENT: This requirement is very important

[REQUIREMENT]
UID: REQ-001
TITLE: Optional title B
STATEMENT: System shall do Y
COMMENT: This requirement is very important
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    print(output)
    assert input == output
