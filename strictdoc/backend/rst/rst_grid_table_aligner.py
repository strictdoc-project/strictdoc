"""
@relation(SDOC-SRS-70, SDOC-SRS-149, scope=file)
"""

import re
from dataclasses import dataclass
from typing import List, Optional

TABLE_LINE_PATTERN = re.compile(r"^\s*[+|]")
BORDER_PATTERN = re.compile(r"^\+(-+\+)+$")
HEADER_BORDER_PATTERN = re.compile(r"^\+(=+\+)+$")


@dataclass
class _GridTable:
    indent: str
    has_header: bool
    # The cells of each row. A cell can hold several lines.
    rows: List[List[str]]
    # The text widths of the columns in the source table.
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

    lines = text.split("\n")
    output: List[str] = []
    index = 0
    while index < len(lines):
        if TABLE_LINE_PATTERN.match(lines[index]) is None:
            output.append(lines[index])
            index += 1
            continue
        end = index
        while end < len(lines) and TABLE_LINE_PATTERN.match(lines[end]):
            end += 1
        block = lines[index:end]
        table = _parse_grid_table(block)
        if table is not None and not table.aligned:
            output.extend(_serialize_grid_table(table))
        else:
            output.extend(block)
        index = end
    return "\n".join(output)


def _parse_grid_table(block_lines: List[str]) -> Optional[_GridTable]:
    if len(block_lines) < 3:
        return None

    indent = _common_indent(block_lines)
    if indent is None:
        return None
    lines = [line_[len(indent) :].rstrip() for line_ in block_lines]

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


def _serialize_grid_table(table: _GridTable) -> List[str]:
    rows = [[_cell_lines(cell_) for cell_ in row_] for row_ in table.rows]
    widths = [
        max(
            1,
            table.column_widths[column_],
            *(len(line_) for row_ in rows for line_ in row_[column_]),
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
                (cell_[line_index] if line_index < len(cell_) else "").ljust(
                    widths[column_]
                )
                for column_, cell_ in enumerate(row)
            ]
            lines.append("| " + " | ".join(cells) + " |")
        is_header = table.has_header and row_index == 0
        lines.append(border("=" if is_header else "-"))
    return [table.indent + line_ for line_ in lines]


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
    indents (lists, directives) stay relative to the cell.
    """

    filled = [part_ for part_ in parts if part_.strip() != ""]
    if len(filled) == 0:
        return ""
    indent = min(len(part_) - len(part_.lstrip(" ")) for part_ in filled)
    return "\n".join(_cell_lines("\n".join(part_[indent:] for part_ in parts)))


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
