from saturn.backend.rst.rst_to_html_writer import HTMLWriter

from saturn.backend.rst.rst_reader import RSTReader


def test_01_basic_test():
    rst_content = """HELLO
=====

WORLD
"""

    expected_html_content = """<h1>HELLO</h1>

WORLD
"""

    writer = HTMLWriter()

    document = RSTReader.read_rst(rst_content)

    rst_document = document.rst_document
    html_lines = writer.write_fragment(rst_document.children)

    assert html_lines == expected_html_content


def test_02_single_text_node():
    rst_content = """HELLO2
"""

    expected_html_content = """HELLO2
"""

    writer = HTMLWriter()

    document = RSTReader.read_rst(rst_content)

    rst_document = document.rst_document
    html_lines = writer.write_fragment(rst_document.children)

    assert html_lines == expected_html_content


def test_03_multiple_text_nodes():
    rst_content = """HELLO1
HELLO2
HELLO3
"""

    expected_html_content = """HELLO1
HELLO2
HELLO3
"""

    writer = HTMLWriter()

    document = RSTReader.read_rst(rst_content)

    rst_document = document.rst_document
    html_lines = writer.write_fragment(rst_document.children)

    assert html_lines == expected_html_content


def test_04_hyperlink():
    rst_content = """HELLO1

`LINK <https://href.href>`_
"""

    expected_html_content = """HELLO1

<a href="https://href.href">LINK</a>
"""

    writer = HTMLWriter()

    document = RSTReader.read_rst(rst_content)

    rst_document = document.rst_document
    html_lines = writer.write_fragment(rst_document.children)

    assert html_lines == expected_html_content


def test_05_multiple_levels_of_headers():
    rst_content = """HELLO1
======

HELLO2
------

HELLO3
~~~~~~

WORLD
"""

    expected_html_content = """<h1>HELLO1</h1>

<h2>HELLO2</h2>

<h3>HELLO3</h3>

WORLD
"""

    writer = HTMLWriter()

    document = RSTReader.read_rst(rst_content)

    rst_document = document.rst_document
    html_lines = writer.write_fragment(rst_document.children)

    assert html_lines == expected_html_content
