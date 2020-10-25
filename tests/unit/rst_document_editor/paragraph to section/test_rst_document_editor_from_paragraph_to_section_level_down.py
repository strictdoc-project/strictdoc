from saturn.backend.rst.rst_reader import RSTReader
from saturn.backend.rst.rst_writer import RSTWriter
from saturn.backend.rst.rst_document_editor import RSTDocumentEditor


def test_00_basic_test():
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

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)

    assert written_rst_content == expected_rst_content


def test_01_level_zero_to_level_one():
    rst_content = """Foo

Bar

HEADER LEVEL 2
--------------

CONTENT LEVEL 2
"""

    new_rst_fragment = """HEADER LEVEL 1
==============
"""

    expected_rst_content = """HEADER LEVEL 1
==============

Bar

HEADER LEVEL 2
--------------

CONTENT LEVEL 2
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    paragraph_1 = lines[0]
    assert paragraph_1.astext() == 'Foo'

    paragraph_2 = lines[1]
    assert paragraph_2.astext() == 'Bar'

    editor.replace_node(paragraph_1, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)

    assert written_rst_content == expected_rst_content
    lines = rst_document.get_as_list()

    assert lines[0].astext() == "HEADER LEVEL 1"
    assert lines[1].astext() == "Bar"
    assert lines[1].parent == lines[0].parent
    assert lines[2].astext() == "HEADER LEVEL 2"
    assert lines[2].parent.parent == lines[1].parent
    assert lines[3].astext() == "CONTENT LEVEL 2"


def test_02_when_level_zero_to_level_one_content_before_stays():
    rst_content = """Foo

Bar

HEADER LEVEL 2
--------------

CONTENT LEVEL 2
"""

    new_rst_fragment = """REPLACED HEADER LEVEL 2
-----------------------
"""

    expected_rst_content = """Foo

REPLACED HEADER LEVEL 2
-----------------------

HEADER LEVEL 2
--------------

CONTENT LEVEL 2
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    paragraph_1 = lines[0]
    assert paragraph_1.astext() == 'Foo'

    paragraph_2 = lines[1]
    assert paragraph_2.astext() == 'Bar'

    editor.replace_node(paragraph_2, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)

    assert written_rst_content == expected_rst_content
    lines = rst_document.get_as_list()

    assert lines[0].astext() == "Foo"
    assert lines[1].astext() == "REPLACED HEADER LEVEL 2"
    assert lines[1].parent.parent == lines[0].parent
    assert lines[2].astext() == "HEADER LEVEL 2"
    assert lines[2].parent.parent == lines[0].parent
    assert lines[3].astext() == "CONTENT LEVEL 2"
