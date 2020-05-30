import docutils.nodes

from strictdoc.backend.rst.rst_parser import RSTParser


def test_01_basic_test():
    rst_content = """HELLO
=====

WORLD
"""

    document = RSTParser.parse_rst(rst_content)

    rst_section = document.children[0]
    assert isinstance(rst_section, docutils.nodes.section)

    rst_title = rst_section.children[0]
    assert isinstance(rst_title, docutils.nodes.title)

    rst_paragraph = rst_section.children[1]
    assert isinstance(rst_paragraph, docutils.nodes.paragraph)


def test_02_only_test():
    rst_content = """HELLO WORLD"""

    document = RSTParser.parse_rst(rst_content)

    paragraph_node = document.children[0]
    assert isinstance(paragraph_node, docutils.nodes.paragraph)

    text_node = paragraph_node.children[0]
    assert isinstance(text_node, docutils.nodes.Text)
    assert text_node.astext(), "HELLO WORLD"


def test_03_only_header():
    rst_content = """HELLO
=====
"""

    document = RSTParser.parse_rst(rst_content)

    section_node = document.children[0]
    assert isinstance(section_node, docutils.nodes.section)

    title_node = section_node.children[0]
    assert isinstance(title_node, docutils.nodes.title)

    text_node = title_node.children[0]
    assert isinstance(text_node, docutils.nodes.Text)
    assert text_node.astext(), "HELLO WORLD"
