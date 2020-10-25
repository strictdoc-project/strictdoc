from saturn.backend.rst.rst_reader import RSTReader


def test_01_basic_test():
    rst_content = """HELLO
=====

WORLD
"""

    document = RSTReader.read_rst(rst_content)

    lines = document.get_as_list()

    assert lines[0].astext() == 'HELLO'
    assert lines[1].astext() == 'WORLD'
