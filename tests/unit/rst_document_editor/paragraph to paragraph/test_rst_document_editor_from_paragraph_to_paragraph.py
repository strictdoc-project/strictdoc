from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.backend.rst.rst_writer import RSTWriter
from strictdoc.backend.rst.rst_document_editor import RSTDocumentEditor


def test_replacing_paragraph_with_paragraph():
    rst_content = """HELLO
=====

OLD CONTENT
"""

    new_rst_fragment = """NEW CONTENT
"""

    expected_rst_content = """HELLO
=====

NEW CONTENT
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    paragraph_node = lines[1]
    assert paragraph_node.astext() == 'OLD CONTENT'

    editor.replace_node(paragraph_node, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content
