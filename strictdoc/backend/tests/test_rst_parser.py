import docutils.nodes

from strictdoc.backend.rst_parser import RSTParser


def test_01_basic_test():
    rst_content = """HELLO
=====

WORLD
"""

    document = RSTParser.parse_rst(rst_content)

    print(document.pformat())

    rst_section = document.children[0]
    assert isinstance(rst_section, docutils.nodes.section)

    rst_title = rst_section.children[0]
    assert isinstance(rst_title, docutils.nodes.title)

    rst_paragraph = rst_section.children[1]
    assert isinstance(rst_paragraph, docutils.nodes.paragraph)
