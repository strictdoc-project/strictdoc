"""
@relation(SDOC-SRS-70, SDOC-SRS-149, SDOC-SRS-213, scope=file)
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from strictdoc.helpers.text_width import is_double_width, text_width

TABLE_LINE_PATTERN = re.compile(r"^\s*[+|]")
BORDER_PATTERN = re.compile(r"^\+(-+\+)+$")
HEADER_BORDER_PATTERN = re.compile(r"^\+(=+\+)+$")
DIRECTIVE_PATTERN = re.compile(r"^\s*\.\. \S+::")
LITERAL_DIRECTIVE_PATTERN = re.compile(
    r"^\s*\.\. (code|code-block|sourcecode)::"
)
# Docutils finds the cell borders of a grid table by the positions of "|" and
# "+" in the lines. A wide character takes the width of two characters (see
# strictdoc.helpers.text_width). Docutils puts a pad character after each
# wide character before it parses the table
# (docutils.statemachine.StringList.pad_double_width()). This module does the
# same, so it measures the positions as docutils does.
DOUBLE_WIDTH_PAD = "\x00"


@dataclass
class _GridTable:
    indent: str
    has_header: bool
    # The cells of each row. A cell can hold several lines.
    rows: List[List[str]]
    # The text widths of the table columns in the source table (see
    # strictdoc.helpers.text_width).
    column_widths: List[int]
    aligned: bool


def align_grid_tables(text: str) -> str:
    """
    Align the misaligned RST grid tables in the text.

    The RST export replaces each inline link with a :ref: role, which is
    longer or shorter than the link source text. In a grid table, this moves
    the "|" of the row, and docutils rejects the table as malformed. This
    function writes such tables again with the borders at the same columns.

    The parser follows the table editor of the Web UI (table_editor.js):
    grid tables without spans and with at most one header row. A row line
    that is not aligned is split on "|". A table that the parser does not
    accept, and a table that is aligned, stay as they are.

    A column keeps at least its width in the source table, so that the
    proportions of the columns change as little as possible.
    """

    return _align_grid_tables(
        text, keep_source_widths=True, skip_literal_blocks=False
    )


def format_grid_tables(text: str) -> str:
    """
    Align the misaligned RST grid tables in the text as the Format table
    button of the Web UI does (table_editor.js).

    The parser is the same as in align_grid_tables(). The serializer follows
    the table editor: a column is as wide as its longest text line, and the
    serializer leaves out an empty header row.

    The tables in literal blocks (after "::", and in the code, code-block,
    and sourcecode directives) stay as they are. Docutils shows a literal
    block as preformatted text and does not parse a grid table in it, so a
    misaligned table in a literal block is not an error. Such a table is an
    example of markup, and its author can make it misaligned on purpose.
    """

    return _align_grid_tables(
        text, keep_source_widths=False, skip_literal_blocks=True
    )


def _align_grid_tables(
    text: str, keep_source_widths: bool, skip_literal_blocks: bool
) -> str:
    lines = text.split("\n")
    in_literal_block = (
        _literal_block_lines(lines)
        if skip_literal_blocks
        else [False] * len(lines)
    )

    def is_table_line(index_: int) -> bool:
        return (
            not in_literal_block[index_]
            and TABLE_LINE_PATTERN.match(lines[index_]) is not None
        )

    output: List[str] = []
    index = 0
    while index < len(lines):
        if not is_table_line(index):
            output.append(lines[index])
            index += 1
            continue
        end = index
        while end < len(lines) and is_table_line(end):
            end += 1
        block = lines[index:end]
        table = _parse_grid_table(block)
        if table is not None and not table.aligned:
            output.extend(_serialize_grid_table(table, keep_source_widths))
        else:
            output.extend(block)
        index = end
    return "\n".join(output)


def _literal_block_lines(lines: List[str]) -> List[bool]:
    """
    Mark the lines of the literal blocks.

    A literal block follows a line that ends with "::" or starts a code,
    code-block, or sourcecode directive. It holds the next lines that are
    blank or indented deeper than that line.
    """

    in_literal_block = [False] * len(lines)
    marker_indent: Optional[int] = None
    for index, line in enumerate(lines):
        if marker_indent is not None:
            if line.strip() == "" or _indent_width(line) > marker_indent:
                in_literal_block[index] = True
                continue
            marker_indent = None
        if LITERAL_DIRECTIVE_PATTERN.match(line) is not None or (
            line.rstrip().endswith("::")
            and DIRECTIVE_PATTERN.match(line) is None
        ):
            marker_indent = _indent_width(line)
    return in_literal_block


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_grid_table(block_lines: List[str]) -> Optional[_GridTable]:
    if len(block_lines) < 3:
        return None

    indent = _common_indent(block_lines)
    if indent is None:
        return None
    lines = [
        _pad_double_width(line_[len(indent) :].rstrip())
        for line_ in block_lines
    ]

    if BORDER_PATTERN.match(lines[0]) is None:
        return None
    edges = [
        position_
        for position_, character_ in enumerate(lines[0])
        if character_ == "+"
    ]
    columns = len(edges) - 1
    column_widths = [
        edges[column_ + 1] - edges[column_] - 3 for column_ in range(columns)
    ]

    has_header = False
    rows: List[List[str]] = []
    row_parts: List[List[str]] = []
    for line_index, line in enumerate(lines[1:], start=1):
        is_border = _border_columns(line, BORDER_PATTERN) == columns
        is_header_border = (
            _border_columns(line, HEADER_BORDER_PATTERN) == columns
        )
        if not is_border and not is_header_border:
            parts = _parse_row_line(line, edges)
            if parts is None:
                return None
            row_parts.append(parts)
            continue
        if len(row_parts) == 0:
            return None
        if is_header_border:
            if len(rows) > 0 or line_index == len(lines) - 1:
                return None
            has_header = True
        rows.append(
            [
                _cell_text([parts_[column_] for parts_ in row_parts])
                for column_ in range(columns)
            ]
        )
        row_parts = []
    if len(row_parts) > 0:
        return None

    aligned = all(
        _is_aligned_line(line_, edges, "+")
        or _is_aligned_line(line_, edges, "|")
        for line_ in lines
    )
    return _GridTable(
        indent=indent,
        has_header=has_header,
        rows=rows,
        column_widths=column_widths,
        aligned=aligned,
    )


def _serialize_grid_table(
    table: _GridTable, keep_source_widths: bool
) -> List[str]:
    """
    Write the table with the borders at the same positions.

    If keep_source_widths is False, the serializer writes the table as the
    table editor of the Web UI does: it leaves out an empty header row (a grid
    table without a header is valid RST) and does not keep the source column
    widths.
    """

    has_header = table.has_header
    source_rows = table.rows
    if (
        not keep_source_widths
        and has_header
        and all(cell_.strip() == "" for cell_ in table.rows[0])
    ):
        has_header = False
        source_rows = table.rows[1:]
    rows = [[_cell_lines(cell_) for cell_ in row_] for row_ in source_rows]
    widths = [
        max(
            1,
            table.column_widths[column_] if keep_source_widths else 1,
            *(text_width(line_) for row_ in rows for line_ in row_[column_]),
        )
        for column_ in range(len(table.column_widths))
    ]

    def border(character: str) -> str:
        return (
            "+" + "+".join(character * (width_ + 2) for width_ in widths) + "+"
        )

    lines = [border("-")]
    for row_index, row in enumerate(rows):
        height = max(len(cell_) for cell_ in row)
        for line_index in range(height):
            cells = [
                _pad_to_width(
                    cell_[line_index] if line_index < len(cell_) else "",
                    widths[column_],
                )
                for column_, cell_ in enumerate(row)
            ]
            lines.append("| " + " | ".join(cells) + " |")
        is_header = has_header and row_index == 0
        lines.append(border("=" if is_header else "-"))
    return [table.indent + line_ for line_ in lines]


def _pad_double_width(line: str) -> str:
    return "".join(
        character_ + DOUBLE_WIDTH_PAD
        if is_double_width(character_)
        else character_
        for character_ in line
    )


def _pad_to_width(text: str, width: int) -> str:
    return text + " " * (width - text_width(text))


def _common_indent(lines: List[str]) -> Optional[str]:
    """
    Return the indent shared by all lines, or None if they differ.

    A line indented deeper than the others also gives None: the serializer
    writes one indent for all lines.
    """

    match = re.match(r"^ *", lines[0])
    assert match is not None
    indent = match.group(0)
    for line_ in lines:
        if not line_.startswith(indent) or line_[len(indent) :].startswith(" "):
            return None
    return indent


def _border_columns(line: str, pattern: re.Pattern[str]) -> int:
    if pattern.match(line) is None:
        return 0
    return len(line.split("+")) - 2


def _is_aligned_line(line: str, edges: List[int], character: str) -> bool:
    return len(line) == edges[-1] + 1 and all(
        line[edge_] == character for edge_ in edges
    )


def _parse_row_line(line: str, edges: List[int]) -> Optional[List[str]]:
    """
    Cut one text line of a row into the parts of its cells.

    An aligned line is cut at the "+" positions of the top border, so a "|"
    inside a cell is plain text. A misaligned line is split on "|" instead.
    The split is accepted only if it gives one part per column: more parts
    mean that a cell contains a "|", and it is unclear where the cells end.
    """

    if _is_aligned_line(line, edges, "|"):
        return [
            line[edges[column_] + 1 : edges[column_ + 1]]
            for column_ in range(len(edges) - 1)
        ]
    if not (len(line) >= 2 and line.startswith("|") and line.endswith("|")):
        return None
    parts = line[1:-1].split("|")
    return parts if len(parts) == len(edges) - 1 else None


def _cell_text(parts: List[str]) -> str:
    """
    Join the parts of a cell from the text lines of its row.

    The indent shared by the non-blank parts is removed, so that nested
    indents (lists, directives) stay relative to the cell. The pad characters
    after the wide characters (see DOUBLE_WIDTH_PAD) are removed too.
    """

    filled = [part_ for part_ in parts if part_.strip() != ""]
    if len(filled) == 0:
        return ""
    indent = min(len(part_) - len(part_.lstrip(" ")) for part_ in filled)
    text = "\n".join(part_[indent:] for part_ in parts)
    return "\n".join(_cell_lines(text.replace(DOUBLE_WIDTH_PAD, "")))


def _cell_lines(cell: str) -> List[str]:
    """
    Split cell text into lines without trailing spaces and without leading
    or trailing blank lines.
    """

    lines = [line_.rstrip() for line_ in cell.split("\n")]
    while len(lines) > 1 and lines[0] == "":
        lines.pop(0)
    while len(lines) > 1 and lines[-1] == "":
        lines.pop()
    return lines
