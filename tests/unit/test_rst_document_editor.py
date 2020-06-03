from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.backend.rst.rst_writer import RSTWriter
from strictdoc.backend.rst.rst_document_editor import RSTDocumentEditor


def test_01_basic_test():
    rst_content = """HELLO
=====

WORLD
"""

    new_rst_fragment = """WORLD
-----
"""

    expected_rst_content = """HELLO
=====

WORLD
-----
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header_node = lines[0]
    assert header_node.astext() == 'HELLO'

    text_node = lines[1]
    assert text_node.astext() == 'WORLD'

    editor.replace_node(text_node, new_rst_fragment)
    print(rst_document.rst_document.pformat())

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)

    assert written_rst_content == expected_rst_content


def test_02_replacing_title_and_its_parent_section_with_paragraph():
    rst_content = """StrictDoc
=========

This is a documentation of StrictDoc written in StrictDoc.

High-level requirements
-----------------------

HEADER3
~~~~~~~

Header-3-content-1

Header-3-content-2
"""

    new_rst_fragment = """Header-3-replacement-paragraph-text"""

    expected_rst_content = """HELLO
=====

WORLD
-----
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header3_title = lines[3]
    assert header3_title.astext() == 'HEADER3'

    editor.replace_node(header3_title, new_rst_fragment)
    # print(rst_document.rst_document.pformat())
    #
    # writer = RSTWriter()
    #
    # written_rst_content = writer.write_rst_document(rst_document.rst_document)
    #
    # assert written_rst_content == expected_rst_content
    #
    #
