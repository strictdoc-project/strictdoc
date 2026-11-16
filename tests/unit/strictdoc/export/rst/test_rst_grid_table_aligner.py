from strictdoc.backend.rst.rst_grid_table_aligner import align_grid_tables


def test_01_misaligned_table_is_aligned():
    text = """\
Text before.

+-------+---------+
| Name  | Value   |
+=======+=========+
| :ref:`Long title <UID>` | A       |
+-------+---------+
| B     | C       |
+-------+---------+

Text after.
"""

    assert (
        align_grid_tables(text)
        == """\
Text before.

+-------------------------+---------+
| Name                    | Value   |
+=========================+=========+
| :ref:`Long title <UID>` | A       |
+-------------------------+---------+
| B                       | C       |
+-------------------------+---------+

Text after.
"""
    )


def test_02_aligned_table_stays_as_is():
    text = """\
+-----------+-----+
| A         | B   |
+-----------+-----+
"""

    assert align_grid_tables(text) == text


def test_03_table_with_spans_stays_as_is():
    text = """\
+-------+-------+
| A spanning    |
+-------+-------+
| :ref:`X <UID>` | C |
+-------+-------+
"""

    assert align_grid_tables(text) == text


def test_04_cell_with_several_lines_and_paragraphs():
    text = """\
   +-----+-----+
   | :ref:`X <UID>` | First |
   | and | line. |
   |     |       |
   |     | Second. |
   +-----+-----+
"""

    assert (
        align_grid_tables(text)
        == """\
   +----------------+---------+
   | :ref:`X <UID>` | First   |
   | and            | line.   |
   |                |         |
   |                | Second. |
   +----------------+---------+
"""
    )


def test_05_cell_with_pipe_in_misaligned_line_stays_as_is():
    text = """\
+-----+-----+
| :ref:`A | B <UID>` | C |
+-----+-----+
"""

    assert align_grid_tables(text) == text
