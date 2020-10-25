from saturn.backend.rst.rst_reader import RSTReader
from saturn.backend.rst.rst_node_finder import RSTNodeFinder


def test_01_moving_level_1_headers():
    rst_content = """HEADER 1
========

Content 1

HEADER 2
========

Content 2

HEADER 3
========

Content 3
"""

    document = RSTReader.read_rst(rst_content)

    lines = document.get_as_list()

    assert lines[0].astext() == 'HEADER 1'
    assert lines[1].astext() == 'Content 1'
    assert lines[2].astext() == 'HEADER 2'
    assert lines[3].astext() == 'Content 2'
    assert lines[4].astext() == 'HEADER 3'
    assert lines[5].astext() == 'Content 3'

    assert RSTNodeFinder.find_new_parent(lines[0].parent, 0) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 1) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 2) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 3) == (document.rst_document, 0)

    assert RSTNodeFinder.find_new_parent(lines[2].parent, 0) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 1) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 2) == (lines[0].parent, -1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 3) == (lines[0].parent, -1)

    assert RSTNodeFinder.find_new_parent(lines[4].parent, 0) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 1) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 2) == (lines[2].parent, -1)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 3) == (lines[2].parent, -1)


def test_02_moving_level_2_headers():
    rst_content = """HEADER 1.1
----------

HEADER 1.2
----------

HEADER 1.3
----------
"""

    document = RSTReader.read_rst(rst_content)

    lines = document.get_as_list()

    assert lines[0].astext() == 'HEADER 1.1'
    assert lines[1].astext() == 'HEADER 1.2'
    assert lines[2].astext() == 'HEADER 1.3'

    section_1_1 = lines[0].parent
    section_1_2 = lines[1].parent

    assert RSTNodeFinder.find_new_parent(lines[0].parent, 0) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 1) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 2) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 3) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 4) == (document.rst_document, 0)

    assert RSTNodeFinder.find_new_parent(lines[1].parent, 0) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[1].parent, 1) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[1].parent, 2) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[1].parent, 3) == (section_1_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[1].parent, 4) == (section_1_1, -1)

    assert RSTNodeFinder.find_new_parent(lines[2].parent, 0) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 1) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 2) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 3) == (section_1_2, -1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 4) == (section_1_2, -1)


def test_03_moving_level_2_headers():
    rst_content = """HEADER 1.1
----------

Content 1.1

HEADER 1.2
----------

Content 1.2

HEADER 1.3
----------

Content 1.3
"""

    document = RSTReader.read_rst(rst_content)

    lines = document.get_as_list()

    assert lines[0].astext() == 'HEADER 1.1'
    assert lines[1].astext() == 'Content 1.1'
    assert lines[2].astext() == 'HEADER 1.2'
    assert lines[3].astext() == 'Content 1.2'
    assert lines[4].astext() == 'HEADER 1.3'
    assert lines[5].astext() == 'Content 1.3'

    section_1_1 = lines[0].parent
    section_1_2 = lines[2].parent

    assert RSTNodeFinder.find_new_parent(lines[0].parent, 0) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 1) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 2) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 3) == (document.rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 4) == (document.rst_document, 0)

    assert RSTNodeFinder.find_new_parent(lines[2].parent, 0) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 1) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 2) == (document.rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 3) == (section_1_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 4) == (section_1_1, -1)

    assert RSTNodeFinder.find_new_parent(lines[4].parent, 0) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 1) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 2) == (document.rst_document, 2)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 3) == (section_1_2, -1)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 4) == (section_1_2, -1)


def test_03_mixed_content():
    rst_content = """HEADER 1
========

Content 1
    
HEADER 1.1
----------

Content 1.1

HEADER 1.1.1
~~~~~~~~~~~~

Content 1.1.1

HEADER 1.2
----------

Content 1.2

HEADER 1.2.1
~~~~~~~~~~~~

Content 1.2.1

HEADER 1.3
----------

Content 1.3

HEADER 1.3.1
~~~~~~~~~~~~

Content 1.3.1

HEADER 2
========

Content 2

HEADER 2.1
----------

Content 2.1

HEADER 2.1.1
~~~~~~~~~~~~

Content 2.1.1

HEADER 2.2
----------

Content 2.2

HEADER 2.2.1
~~~~~~~~~~~~

Content 2.2.1

HEADER 2.3
----------

Content 2.3

HEADER 2.3.1
~~~~~~~~~~~~

Content 2.3.1
"""

    document = RSTReader.read_rst(rst_content)

    lines = document.get_as_list()

    assert lines[0].astext() == 'HEADER 1'
    assert lines[1].astext() == 'Content 1'
    assert lines[2].astext() == 'HEADER 1.1'
    assert lines[3].astext() == 'Content 1.1'
    assert lines[4].astext() == 'HEADER 1.1.1'
    assert lines[5].astext() == 'Content 1.1.1'
    assert lines[6].astext() == 'HEADER 1.2'
    assert lines[7].astext() == 'Content 1.2'
    assert lines[8].astext() == 'HEADER 1.2.1'
    assert lines[9].astext() == 'Content 1.2.1'
    assert lines[10].astext() == 'HEADER 1.3'
    assert lines[11].astext() == 'Content 1.3'
    assert lines[12].astext() == 'HEADER 1.3.1'
    assert lines[13].astext() == 'Content 1.3.1'

    assert lines[14].astext() == 'HEADER 2'
    assert lines[15].astext() == 'Content 2'
    assert lines[16].astext() == 'HEADER 2.1'
    assert lines[17].astext() == 'Content 2.1'
    assert lines[18].astext() == 'HEADER 2.1.1'
    assert lines[19].astext() == 'Content 2.1.1'
    assert lines[20].astext() == 'HEADER 2.2'
    assert lines[21].astext() == 'Content 2.2'
    assert lines[22].astext() == 'HEADER 2.2.1'
    assert lines[23].astext() == 'Content 2.2.1'
    assert lines[24].astext() == 'HEADER 2.3'
    assert lines[25].astext() == 'Content 2.3'
    assert lines[26].astext() == 'HEADER 2.3.1'
    assert lines[27].astext() == 'Content 2.3.1'

    rst_document = document.rst_document

    section_1 = lines[0].parent
    section_1_1 = lines[2].parent
    section_1_1_1 = lines[4].parent
    section_1_2 = lines[6].parent
    section_1_2_1 = lines[8].parent
    section_1_3 = lines[10].parent
    section_1_3_1 = lines[12].parent
    section_2 = lines[14].parent
    section_2_1 = lines[16].parent
    section_2_1_1 = lines[18].parent

    assert RSTNodeFinder.find_new_parent(lines[0].parent, 0) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 1) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 2) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 3) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[0].parent, 4) == (rst_document, 0)

    assert RSTNodeFinder.find_new_parent(lines[2].parent, 0) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 1) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 2) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 3) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[2].parent, 4) == (section_1, -1)

    assert lines[4].astext() == 'HEADER 1.1.1'
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 0) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 1) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 2) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 3) == (section_1_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[4].parent, 4) == (section_1_1, -1)

    assert lines[6].astext() == 'HEADER 1.2'
    assert RSTNodeFinder.find_new_parent(lines[6].parent, 0) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[6].parent, 1) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[6].parent, 2) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[6].parent, 3) == (section_1_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[6].parent, 4) == (section_1_1_1, -1)

    assert lines[8].astext() == 'HEADER 1.2.1'
    assert RSTNodeFinder.find_new_parent(lines[8].parent, 0) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[8].parent, 1) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[8].parent, 2) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[8].parent, 3) == (section_1_2, -1)
    assert RSTNodeFinder.find_new_parent(lines[8].parent, 4) == (section_1_2, -1)

    assert lines[10].astext() == 'HEADER 1.3'
    assert RSTNodeFinder.find_new_parent(lines[10].parent, 0) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[10].parent, 1) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[10].parent, 2) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[10].parent, 3) == (section_1_2, -1)
    assert RSTNodeFinder.find_new_parent(lines[10].parent, 4) == (section_1_2_1, -1)

    assert lines[12].astext() == 'HEADER 1.3.1'
    assert RSTNodeFinder.find_new_parent(lines[12].parent, 0) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[12].parent, 1) == (rst_document, 0)
    assert RSTNodeFinder.find_new_parent(lines[12].parent, 2) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[12].parent, 3) == (section_1_3, -1)
    assert RSTNodeFinder.find_new_parent(lines[12].parent, 4) == (section_1_3, -1)

    assert lines[14].astext() == 'HEADER 2'
    assert RSTNodeFinder.find_new_parent(lines[14].parent, 0) == (rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[14].parent, 1) == (rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[14].parent, 2) == (section_1, -1)
    assert RSTNodeFinder.find_new_parent(lines[14].parent, 3) == (section_1_3, -1)
    assert RSTNodeFinder.find_new_parent(lines[14].parent, 4) == (section_1_3_1, -1)

    assert lines[16].astext() == 'HEADER 2.1'
    assert RSTNodeFinder.find_new_parent(lines[16].parent, 0) == (rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[16].parent, 1) == (rst_document, 1)
    assert RSTNodeFinder.find_new_parent(lines[16].parent, 2) == (section_2, -1)
    assert RSTNodeFinder.find_new_parent(lines[16].parent, 3) == (section_2, -1)
    assert RSTNodeFinder.find_new_parent(lines[16].parent, 4) == (section_2, -1)
