from docutils.core import publish_parts

from strictdoc.backend.rst.rst_grid_table_aligner import (
    align_grid_tables,
    format_grid_tables,
)


def assert_docutils_accepts(text: str) -> None:
    publish_parts(
        text,
        writer="html",
        settings_overrides={"report_level": 5, "halt_level": 2},
    )


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


def test_06_format_fits_columns_to_text():
    text = """\
+------------+-------+
| Name | Value |
+============+=======+
| A          | B     |
+------------+-------+
"""

    assert (
        format_grid_tables(text)
        == """\
+------+-------+
| Name | Value |
+======+=======+
| A    | B     |
+------+-------+
"""
    )


def test_07_format_leaves_out_empty_header_row():
    text = """\
+-----+-----+
|     |  |
+=====+=====+
| A | B   |
+-----+-----+
"""

    assert (
        format_grid_tables(text)
        == """\
+---+---+
| A | B |
+---+---+
"""
    )


def test_08_format_keeps_aligned_table():
    text = """\
+-----------+-----+
| A         | B   |
+-----------+-----+
"""

    assert format_grid_tables(text) == text


def test_09_format_skips_literal_blocks():
    text = """\
Example::

    +-----+-----+
    | A | B |
    +-----+-----+

.. code-block:: text

    +-----+-----+
    | A | B |
    +-----+-----+

.. code:: text
   :linenos:

   +-----+-----+
   | A | B |
   +-----+-----+

+-----+-----+
| A | B |
+-----+-----+
"""

    assert (
        format_grid_tables(text)
        == """\
Example::

    +-----+-----+
    | A | B |
    +-----+-----+

.. code-block:: text

    +-----+-----+
    | A | B |
    +-----+-----+

.. code:: text
   :linenos:

   +-----+-----+
   | A | B |
   +-----+-----+

+---+---+
| A | B |
+---+---+
"""
    )


def test_10_format_aligns_table_in_table_directive():
    text = """\
.. table:: Caption
   :widths: 40 60

   +-----+-----+
   | A | B |
   +-----+-----+

.. table::

   +-----+-----+
   | C | D |
   +-----+-----+
"""

    assert (
        format_grid_tables(text)
        == """\
.. table:: Caption
   :widths: 40 60

   +---+---+
   | A | B |
   +---+---+

.. table::

   +---+---+
   | C | D |
   +---+---+
"""
    )


def test_11_wide_character_takes_width_of_two_characters():
    text = """\
+--+--+
| A | B |
+--+--+
| 😀 | 中文 |
+--+--+
| abc | x |
+--+--+
"""

    output = format_grid_tables(text)
    assert (
        output
        == """\
+-----+------+
| A   | B    |
+-----+------+
| 😀  | 中文 |
+-----+------+
| abc | x    |
+-----+------+
"""
    )
    assert_docutils_accepts(output)
    assert format_grid_tables(output) == output


def test_12_table_aligned_with_wide_characters_stays_as_is():
    text = """\
+----+---+
| A  | B |
+----+---+
| 😀 | x |
+----+---+
"""

    assert_docutils_accepts(text)
    assert format_grid_tables(text) == text
    assert align_grid_tables(text) == text


def test_13_align_counts_wide_characters():
    text = """\
+------+-----+
| 中文 :ref:`T <X>` | A |
+------+-----+
"""

    assert (
        align_grid_tables(text)
        == """\
+-------------------+-----+
| 中文 :ref:`T <X>` | A   |
+-------------------+-----+
"""
    )
