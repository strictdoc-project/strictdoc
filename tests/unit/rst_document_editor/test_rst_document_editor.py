from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.backend.rst.rst_writer import RSTWriter
from strictdoc.backend.rst.rst_document_editor import RSTDocumentEditor


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

    expected_rst_content = """StrictDoc
=========

This is a documentation of StrictDoc written in StrictDoc.

High-level requirements
-----------------------

Header-3-replacement-paragraph-text

Header-3-content-1

Header-3-content-2
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header3_title = lines[3]
    assert header3_title.astext() == 'HEADER3'

    editor.replace_node(header3_title, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)

    assert written_rst_content == expected_rst_content


def test_03_replacing_header_1_with_header_2():
    rst_content = """HEADER1
=======

Paragraph content
"""

    new_rst_fragment = """HEADER2
-------    
"""

    expected_rst_content = """HEADER2
-------

Paragraph content
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header1_title = lines[0]
    assert header1_title.astext() == 'HEADER1'

    editor.replace_node(header1_title, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content
