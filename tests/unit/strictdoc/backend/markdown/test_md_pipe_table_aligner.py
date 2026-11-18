from strictdoc.backend.markdown.md_pipe_table_aligner import (
    format_pipe_tables,
)


def test_01_misaligned_table_is_aligned():
    text = """\
Text before.

| Name | Value |
|---|---|
| Long name | A |
| B | C |

Text after.
"""

    assert (
        format_pipe_tables(text)
        == """\
Text before.

| Name      | Value |
| --------- | ----- |
| Long name | A     |
| B         | C     |

Text after.
"""
    )


def test_02_aligned_table_stays_as_is():
    text = """\
| A         | B   |
| --------- | --- |
| C         | D   |
"""

    assert format_pipe_tables(text) == text


def test_03_alignment_markers_are_kept():
    text = """\
| Left | Center | Right | None |
|:-|:-:|-:|-|
| a | b | c | d |
"""

    assert (
        format_pipe_tables(text)
        == """\
| Left | Center | Right | None |
| :--- | :----: | ----: | ---- |
| a    | b      | c     | d    |
"""
    )


def test_04_rows_without_outer_pipes_and_missing_cells():
    text = """\
A | B | C
--- | --- | ---
1 | 2
"""

    assert (
        format_pipe_tables(text)
        == """\
| A   | B   | C   |
| --- | --- | --- |
| 1   | 2   |     |
"""
    )


def test_05_escaped_pipes_and_line_breaks():
    text = """\
| Code | Text |
|---|---|
| `a \\| b` | First<br/>second |
"""

    assert (
        format_pipe_tables(text)
        == """\
| Code     | Text            |
| -------- | --------------- |
| `a \\| b` | First<br>second |
"""
    )


def test_06_table_in_fenced_code_block_stays_as_is():
    text = """\
```
| A | B |
|-|-|
| C | D |
```
"""

    assert format_pipe_tables(text) == text


def test_07_extra_cells_of_a_row_become_columns():
    text = """\
| A | B |
|---|---|
| C | D | E |
"""

    assert (
        format_pipe_tables(text)
        == """\
| A   | B   |     |
| --- | --- | --- |
| C   | D   | E   |
"""
    )


def test_08_table_ends_at_block_start():
    text = """\
| A | B |
|-|-|
| C | D |
- List item
"""

    assert (
        format_pipe_tables(text)
        == """\
| A   | B   |
| --- | --- |
| C   | D   |
- List item
"""
    )


def test_09_indented_table_keeps_indent():
    text = """\
  | A | B |
  |-|-|
  | C | D |
"""

    assert (
        format_pipe_tables(text)
        == """\
  | A   | B   |
  | --- | --- |
  | C   | D   |
"""
    )


def test_10_wide_character_takes_width_of_two_characters():
    text = """\
| A | B |
|-|-|
| 😀 | 中文 |
| ab | y |
"""

    assert (
        format_pipe_tables(text)
        == """\
| A   | B    |
| --- | ---- |
| 😀  | 中文 |
| ab  | y    |
"""
    )


def test_11_aligned_table_with_wide_characters_stays_as_is():
    text = """\
| A   | B    |
| --- | ---- |
| 😀  | 中文 |
"""

    assert format_pipe_tables(text) == text
