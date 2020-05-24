import docutils.nodes

from strictdoc.backend.rst.docutils_helper import DocutilsHelper
from strictdoc.backend.rst.rst_writer import RSTWriter
from strictdoc.backend.rst.rst_reader import RSTReader


def test_01_basic_test():
    rst_content = """HELLO
=====
"""

    writer = RSTWriter()

    document = RSTReader.read_rst(rst_content)

    rst_document = document.rst_document
    html_lines = writer.write_rst_fragment(rst_document.children)

    assert html_lines == rst_content


def test_99_regression_printing_rst_of_level_3_headers():
    rst_content = """StrictDoc
=========

This is a documentation of StrictDoc written in StrictDoc.

High-level requirements
-----------------------

HEADER3
~~~~~~~
"""

    expected_rst_content = """HEADER3
~~~~~~~
"""

    writer = RSTWriter()

    document = RSTReader.read_rst(rst_content)

    title_node = document.rst_document.children[0].children[2].children[1].children[0]
    assert isinstance(title_node, docutils.nodes.title)
    assert title_node.astext(), "TODO"

    html_lines = writer.write_rst_fragment(title_node)

    assert html_lines == expected_rst_content
