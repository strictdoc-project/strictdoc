from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.backend.rst.rst_document_editor import RSTDocumentEditor
from strictdoc.backend.rst.rst_writer import RSTWriter
from strictdoc.core.logger import Logger

Logger.enabled_loggers = ['RSTDocumentEditor']

def test_01_transforming_header_level_1_to_paragraph_level_0_with_preceding_header():
    rst_content = """HEADER LEVEL 1
==============

HEADER LEVEL 2
==============

PARAGRAPH WILL MOVE TOGETHER

HEADER LEVEL 2.1
----------------

HEADER LEVEL 3
==============
"""

    new_rst_fragment = """REPLACED PARAGRAPH
"""

    expected_rst_content = """HEADER LEVEL 1
==============

REPLACED PARAGRAPH

PARAGRAPH WILL MOVE TOGETHER

HEADER LEVEL 2.1
----------------

HEADER LEVEL 3
==============
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header_level_2 = lines[1]
    assert header_level_2.astext() == 'HEADER LEVEL 2'

    editor.replace_node(header_level_2, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[1].parent == lines[0].parent


def test_02_transforming_header_level_1_to_paragraph_level_0_no_preceding_header():
    rst_content = """HEADER LEVEL 1
==============

PARAGRAPH LEVEL 1

HEADER LEVEL 2.1
----------------

HEADER LEVEL 3
==============
"""

    new_rst_fragment = """REPLACED PARAGRAPH
"""

    expected_rst_content = """REPLACED PARAGRAPH

PARAGRAPH LEVEL 1

HEADER LEVEL 2.1
----------------

HEADER LEVEL 3
==============
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header_level_2 = lines[0]
    assert header_level_2.astext() == 'HEADER LEVEL 1'

    editor.replace_node(header_level_2, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'REPLACED PARAGRAPH'
    assert lines[0].parent == rst_document.rst_document

    assert lines[1].astext() == 'PARAGRAPH LEVEL 1'
    assert lines[1].parent == rst_document.rst_document

    assert lines[2].astext() == 'HEADER LEVEL 2.1'
    assert lines[2].parent.parent == rst_document.rst_document

    assert lines[3].astext() == 'HEADER LEVEL 3'
    assert lines[3].parent.parent == rst_document.rst_document


def test_03_transforming_header_level_1_to_paragraph_level_0_no_preceding_header():
    rst_content = """HEADER LEVEL 1
==============

PARAGRAPH LEVEL 1

HEADER LEVEL 1.1
----------------

PARAGRAPH LEVEL 1.1

HEADER LEVEL 1.2
----------------

PARAGRAPH LEVEL 1.2
"""

    new_rst_fragment = """REPLACED PARAGRAPH
"""

    expected_rst_content = """HEADER LEVEL 1
==============

PARAGRAPH LEVEL 1

REPLACED PARAGRAPH

PARAGRAPH LEVEL 1.1

HEADER LEVEL 1.2
----------------

PARAGRAPH LEVEL 1.2
"""

    rst_document = RSTReader.read_rst(rst_content)
    editor = RSTDocumentEditor(rst_document)

    lines = rst_document.get_as_list()

    header_level_2 = lines[2]
    assert header_level_2.astext() == 'HEADER LEVEL 1.1'

    editor.replace_node(header_level_2, new_rst_fragment)

    writer = RSTWriter()

    written_rst_content = writer.write_rst_document(rst_document.rst_document)
    assert written_rst_content == expected_rst_content

    lines = rst_document.get_as_list()

    assert lines[0].astext() == 'HEADER LEVEL 1'
    assert lines[0].parent.parent == rst_document.rst_document

    assert lines[1].astext() == 'PARAGRAPH LEVEL 1'
    assert lines[1].parent == lines[0].parent

    assert lines[2].astext() == 'REPLACED PARAGRAPH'
    assert lines[2].parent == lines[0].parent

    assert lines[3].astext() == 'PARAGRAPH LEVEL 1.1'
    assert lines[3].parent == lines[0].parent

    assert lines[4].astext() == 'HEADER LEVEL 1.2'
    assert lines[4].parent.parent == lines[0].parent

    assert lines[5].astext() == 'PARAGRAPH LEVEL 1.2'
    assert lines[5].parent == lines[4].parent
