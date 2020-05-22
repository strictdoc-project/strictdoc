from strictdoc.backend.rst.rst_reader import RSTReader


def test_01_basic_test():
    rst_content = """HELLO
=====

WORLD
"""

    document = RSTReader.read_rst(rst_content)

    lines = document.get_as_list()

    assert lines[0] == 'HELLO'
    assert lines[1] == 'WORLD'


def test_02_nested_headers_additional_information_available():
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

    assert lines[0] == 'HELLO1'
    assert lines[1] == 'HELLO2'
    assert lines[2] == 'HELLO3'
    assert lines[3] == 'WORLD'

    section_level_1 = document.rst_document.children[0]
    assert section_level_1['strictdoc_level'] == 1

    section_level_2 = section_level_1.children[1]
    assert section_level_2['strictdoc_level'] == 2

    section_level_3 = section_level_2.children[1]
    assert section_level_3['strictdoc_level'] == 3
