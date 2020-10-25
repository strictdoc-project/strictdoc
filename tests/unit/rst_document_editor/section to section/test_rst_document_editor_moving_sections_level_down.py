from saturn.backend.rst.rst_constants import SATURN_ATTR_LEVEL
from saturn.backend.rst.rst_document_editor import RSTDocumentEditor
from saturn.backend.rst.rst_reader import RSTReader
from saturn.backend.rst.rst_writer import RSTWriter


def test_04_replacing_header_1_with_header_2_children_behavior():
    rst_content = """HEADER 1
========

1 Paragraph content

HEADER 2
========

2 Paragraph content

HEADER 2.1
----------

2.1 Paragraph content
"""

    new_rst_fragment = """REPLACED HEADER 1.1
-------------------
"""

    expected_rst_content = """HEADER 1
========

1 Paragraph content

REPLACED HEADER 1.1
-------------------

2 Paragraph content

HEADER 2.1
----------

2.1 Paragraph content
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header1_title = lines[0]
    header2_title = lines[2]
    assert header1_title.astext() == 'HEADER 1'
    assert header2_title.astext() == 'HEADER 2'

    editor.replace_node(header2_title, new_rst_fragment)
    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'HEADER 1'
    assert lines[0].parent[SATURN_ATTR_LEVEL] == 1

    assert lines[1].astext() == '1 Paragraph content'

    assert lines[2].astext() == 'REPLACED HEADER 1.1'
    assert lines[2].parent[SATURN_ATTR_LEVEL] == 2

    assert lines[3].astext() == '2 Paragraph content'

    assert lines[4].astext() == 'HEADER 2.1'
    assert lines[4].parent[SATURN_ATTR_LEVEL] == 2

    assert lines[5].astext() == '2.1 Paragraph content'


def test_05_replacing_header_1_with_header_3_children_behavior():
    rst_content = """HEADER 1
========

1 Paragraph content

HEADER 2
========

2 Paragraph content

HEADER 2.1
----------

2.1 Paragraph content
"""

    new_rst_fragment = """HEADER 1.1.1
~~~~~~~~~~~~
"""

    expected_rst_content = """HEADER 1
========

1 Paragraph content

HEADER 1.1.1
~~~~~~~~~~~~

2 Paragraph content

HEADER 2.1
----------

2.1 Paragraph content
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header1_title = lines[0]
    header2_title = lines[2]
    assert header1_title.astext() == 'HEADER 1'
    assert header2_title.astext() == 'HEADER 2'

    editor.replace_node(header2_title, new_rst_fragment)
    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'HEADER 1'
    assert lines[0].parent[SATURN_ATTR_LEVEL] == 1

    assert lines[1].astext() == '1 Paragraph content'

    assert lines[2].astext() == 'HEADER 1.1.1'
    assert lines[2].parent[SATURN_ATTR_LEVEL] == 3

    assert lines[2].parent.parent == lines[0].parent

    assert lines[3].astext() == '2 Paragraph content'

    assert lines[4].astext() == 'HEADER 2.1'
    assert lines[4].parent[SATURN_ATTR_LEVEL] == 2
    assert lines[4].parent.parent == lines[0].parent

    assert lines[5].astext() == '2.1 Paragraph content'


def test_06_wip_replacing_header_2_with_header_1_children_behavior():
    rst_content = """HEADER LEVEL 2 #1
-----------------

LEVEL 2 CONTENT #1

HEADER LEVEL 2 #2
-----------------

LEVEL 2 CONTENT #2

HEADER LEVEL 2 #3
-----------------

LEVEL 2 CONTENT #3
"""

    expected_rst_content = """REPLACED HEADER LEVEL 4
^^^^^^^^^^^^^^^^^^^^^^^

LEVEL 2 CONTENT #1

HEADER LEVEL 2 #2
-----------------

LEVEL 2 CONTENT #2

HEADER LEVEL 2 #3
-----------------

LEVEL 2 CONTENT #3
"""

    new_rst_fragment = """REPLACED HEADER LEVEL 4
^^^^^^^^^^^^^^^^^^^^^^^
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    node1 = lines[0]
    node2 = lines[1]
    assert node1.astext() == 'HEADER LEVEL 2 #1'
    assert node2.astext() == 'LEVEL 2 CONTENT #1'

    editor.replace_node(node1, new_rst_fragment)

    writer = RSTWriter()
    written_rst_content = writer.write_rst_document(rst_document.rst_document)

    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'REPLACED HEADER LEVEL 4'
    assert lines[0].parent[SATURN_ATTR_LEVEL] == 4

    assert lines[1].astext() == 'LEVEL 2 CONTENT #1'
