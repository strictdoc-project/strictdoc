from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.backend.rst.rst_node_finder import RSTNodeFinder


def test_01():
    rst_content = """HELLO1
======

HELLO2
------

HELLO3
~~~~~~

WORLD
"""

    document = RSTReader.read_rst(rst_content)

    lines = document.get_as_list()

    assert lines[0].astext() == 'HELLO1'
    assert lines[1].astext() == 'HELLO2'
    assert lines[2].astext() == 'HELLO3'
    assert lines[3].astext() == 'WORLD'

    assert RSTNodeFinder.find_parent_of_level(lines[2].parent, 0), document.rst_document
    assert RSTNodeFinder.find_parent_of_level(lines[2].parent, 1), lines[0].parent
    assert RSTNodeFinder.find_parent_of_level(lines[2].parent, 2), lines[1].parent
