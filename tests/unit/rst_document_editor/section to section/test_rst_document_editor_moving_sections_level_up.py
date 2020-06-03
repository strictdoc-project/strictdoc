from strictdoc.backend.rst.rst_constants import STRICTDOC_ATTR_LEVEL
from strictdoc.backend.rst.rst_document_editor import RSTDocumentEditor
from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.backend.rst.rst_writer import RSTWriter


def test_01_replacing_header_2_with_header_1_children_behavior():
    rst_content = """HEADER 1
========

1 Paragraph content

HEADER 1.1
----------

1.1 Paragraph content

HEADER 1.2
----------

1.2 Paragraph content
"""

    expected_rst_content = """HEADER 1
========

1 Paragraph content

HEADER 2
========

1.1 Paragraph content

HEADER 1.2
----------

1.2 Paragraph content
"""

    new_rst_fragment = """HEADER 2
========
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header1_title = lines[0]
    header2_title = lines[2]
    assert header1_title.astext() == 'HEADER 1'
    assert header2_title.astext() == 'HEADER 1.1'

    editor.replace_node(header2_title, new_rst_fragment)
    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'HEADER 1'
    assert lines[0].parent[STRICTDOC_ATTR_LEVEL] == 1

    assert lines[1].astext() == '1 Paragraph content'

    assert lines[2].astext() == 'HEADER 2'
    assert lines[2].parent[STRICTDOC_ATTR_LEVEL] == 1

    assert lines[3].astext() == '1.1 Paragraph content'

    assert lines[4].astext() == 'HEADER 1.2'
    assert lines[4].parent[STRICTDOC_ATTR_LEVEL] == 2

    assert lines[5].astext() == '1.2 Paragraph content'


def test_02_replacing_header_3_with_header_1_children_behavior():
    rst_content = """HEADER 1
========

1 Paragraph content

HEADER 1.1
----------

1.1 Paragraph content

HEADER 1.1.1
~~~~~~~~~~~~

1.1.1 Paragraph content

HEADER 1.2
----------

1.2 Paragraph content
"""

    expected_rst_content = """HEADER 1
========

1 Paragraph content

HEADER 1.1
----------

1.1 Paragraph content

NEW LEVEL 1 HEADER
==================

1.1.1 Paragraph content

HEADER 1.2
----------

1.2 Paragraph content
"""

    new_rst_fragment = """NEW LEVEL 1 HEADER
==================
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header1_title = lines[0]
    header_1_1_title = lines[2]
    header_1_1_1_title = lines[4]
    assert header1_title.astext() == 'HEADER 1'
    assert header_1_1_title.astext() == 'HEADER 1.1'
    assert header_1_1_1_title.astext() == 'HEADER 1.1.1'

    editor.replace_node(header_1_1_1_title, new_rst_fragment)
    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'HEADER 1'
    assert lines[0].parent[STRICTDOC_ATTR_LEVEL] == 1
    assert lines[1].astext() == '1 Paragraph content'

    assert lines[2].astext() == 'HEADER 1.1'
    assert lines[2].parent[STRICTDOC_ATTR_LEVEL] == 2
    assert lines[3].astext() == '1.1 Paragraph content'

    assert lines[4].astext() == 'NEW LEVEL 1 HEADER'
    assert lines[4].parent[STRICTDOC_ATTR_LEVEL] == 1
    assert lines[5].astext() == '1.1.1 Paragraph content'

    assert lines[6].astext() == 'HEADER 1.2'
    assert lines[6].parent[STRICTDOC_ATTR_LEVEL] == 2

    assert lines[7].astext() == '1.2 Paragraph content'


def test_03_replacing_header_2_with_header_1_children_behavior():
    rst_content = """HEADER LEVEL 1.1
----------------

PARAGRAPH CONTENT LEVEL 1.1

HEADER LEVEL 1.2
----------------

PARAGRAPH CONTENT LEVEL 1.2
"""

    expected_rst_content = """REPLACED HEADER 1
=================

PARAGRAPH CONTENT LEVEL 1.1

HEADER LEVEL 1.2
----------------

PARAGRAPH CONTENT LEVEL 1.2
"""

    new_rst_fragment = """REPLACED HEADER 1
=================
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    node1 = lines[0]
    node2 = lines[1]
    assert node1.astext() == 'HEADER LEVEL 1.1'
    assert node2.astext() == 'PARAGRAPH CONTENT LEVEL 1.1'

    editor.replace_node(node1, new_rst_fragment)

    writer = RSTWriter()
    written_rst_content = writer.write_rst_document(rst_document.rst_document)

    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'REPLACED HEADER 1'
    assert lines[0].parent[STRICTDOC_ATTR_LEVEL] == 1

    assert lines[1].astext() == 'PARAGRAPH CONTENT LEVEL 1.1'

    assert lines[2].astext() == 'HEADER LEVEL 1.2'
    assert lines[2].parent[STRICTDOC_ATTR_LEVEL] == 2

    assert lines[3].astext() == 'PARAGRAPH CONTENT LEVEL 1.2'
