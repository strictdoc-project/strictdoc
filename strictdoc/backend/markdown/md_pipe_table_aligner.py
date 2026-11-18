"""
@relation(SDOC-SRS-213, scope=file)
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from strictdoc.helpers.text_width import text_width

# The table rules follow the table editor of the Web UI (table_editor.js),
# which follows the table rule of markdown-it (GFM):
# - A table starts with a header row that contains "|" and a delimiter row
#   with the same number of cells.
# - Every following line is a row, even without "|", up to a blank line, a
#   line indented by four or more spaces (code), or the start of another
#   block (BLOCK_START_PATTERNS).
# - A row can have fewer cells than the header: the missing cells are empty.
#   A row can have more cells: markdown-it does not show the extra cells.
#
# The widths and the "|" positions are measured in text width, as in RST
# grid tables: a wide character, for example, a CJK character or an emoji,
# takes the width of two characters (see strictdoc.helpers.text_width).
# markdown-it does not use the "|" positions. But with this measure, a table
# looks aligned in a monospace font, and the RST and Markdown tables follow
# one rule.
#
# The data in the table rows is the source of truth, not the number of
# columns in the header row. A table has as many columns as its widest row.
# The parser adds empty cells to the header row, to the delimiter row, and
# to the shorter rows. As a result, the extra cells of a row become columns,
# and the serializer writes the text of every cell.
DELIMITER_CELL_PATTERN = re.compile(r"^:?-+:?$")
# A delimiter row has only "|", "-", ":", and spaces. A row that starts with
# "-" and a space is a list item.
DELIMITER_ROW_PATTERN = re.compile(r"^[|:-][|:\- \t]*$")
LIST_ITEM_DASH_PATTERN = re.compile(r"^-[ \t]")
# A pipe table row is one text line: line breaks inside a cell are <br>.
LINE_BREAK_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)
FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
# The HTML block names of markdown-it (common/html_blocks.py).
HTML_BLOCK_NAMES = (
    "address|article|aside|base|basefont|blockquote|body|caption|"
    "center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|"
    "figure|footer|form|frame|frameset|h1|h2|h3|h4|h5|h6|head|header|hr|html|"
    "iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|"
    "p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|"
    "track|ul"
)
# The starts of the blocks that end a table, tested on a line without its
# indent: fence, blockquote, thematic break, list item, heading, and the HTML
# blocks that can end a paragraph.
BLOCK_START_PATTERNS = [
    re.compile(r"^(`{3,}|~{3,})"),
    re.compile(r"^>"),
    re.compile(r"^([-*_])([ \t]*\1){2,}[ \t]*$"),
    re.compile(r"^([-*+]|\d{1,9}[.)])([ \t]|$)"),
    re.compile(r"^#{1,6}([ \t]|$)"),
    re.compile(r"^<(script|pre|style|textarea)(?=(\s|>|$))", re.IGNORECASE),
    re.compile(r"^<!--"),
    re.compile(r"^<\?"),
    re.compile(r"^<![A-Z]"),
    re.compile(r"^<!\[CDATA\["),
    re.compile(rf"^</?({HTML_BLOCK_NAMES})(?=(\s|/?>|$))", re.IGNORECASE),
]


@dataclass
class _PipeTable:
    indent: str
    # The cells of each row, padded to the widest row. Row 0 is the header
    # row. A cell can hold several lines.
    rows: List[List[str]]
    # "left", "right", "center", or "" for each column.
    align: List[str]
    aligned: bool


def format_pipe_tables(text: str) -> str:
    """
    Align the misaligned Markdown pipe tables in the text as the Format table
    button of the Web UI does (table_editor.js).

    A table is aligned when the "|" of all its lines stand at the same
    positions. A table that the parser does not accept, and a table that is
    aligned, stay as they are.

    The tables in fenced code blocks also stay as they are. markdown-it shows
    a fenced code block as preformatted text and does not parse a table in
    it. Such a table is an example of markup, and its author can make it
    misaligned on purpose.

    A table has as many columns as its widest row (see the comment at the top
    of this module).
    """

    lines = text.split("\n")
    in_fence = _fenced_lines(lines)
    output: List[str] = []
    index = 0
    while index < len(lines):
        end = _table_end(lines, in_fence, index)
        table = _parse_pipe_table(lines[index:end]) if end is not None else None
        if end is None or table is None:
            output.append(lines[index])
            index += 1
            continue
        if table.aligned:
            output.extend(lines[index:end])
        else:
            output.extend(_serialize_pipe_table(table))
        index = end
    return "\n".join(output)


def _fenced_lines(lines: List[str]) -> List[bool]:
    in_fence = [False] * len(lines)
    fence: Optional[str] = None
    for index, line in enumerate(lines):
        match = FENCE_PATTERN.match(line)
        if fence is None and match is not None:
            fence = match.group(1)[0]
            in_fence[index] = True
        elif fence is not None:
            in_fence[index] = True
            if match is not None and match.group(1)[0] == fence:
                fence = None
    return in_fence


def _table_end(
    lines: List[str], in_fence: List[bool], start: int
) -> Optional[int]:
    """
    Return the end (exclusive) of the table candidate that starts at the
    line `start`, or None if no table starts there.
    """

    if start + 1 >= len(lines):
        return None
    if (
        in_fence[start]
        or in_fence[start + 1]
        or _indent_width(lines[start]) >= 4
        or "|" not in lines[start]
        or not _is_delimiter_row(lines[start + 1])
    ):
        return None
    end = start + 2
    while end < len(lines) and not in_fence[end] and _is_table_row(lines[end]):
        end += 1
    return end


def _parse_pipe_table(block_lines: List[str]) -> Optional[_PipeTable]:
    header, delimiter, *body = [_split_pipe_row(line_) for line_ in block_lines]
    if not all(DELIMITER_CELL_PATTERN.match(cell_) for cell_ in delimiter):
        return None
    if len(header) != len(delimiter):
        return None

    columns = max([len(header)] + [len(row_) for row_ in body])

    def pad(cells: List[str]) -> List[str]:
        return cells + [""] * (columns - len(cells))

    first_positions = _pipe_positions(block_lines[0])
    return _PipeTable(
        # The serializer writes all lines with the indent of the header.
        indent=" " * _indent_width(block_lines[0]),
        rows=[
            [LINE_BREAK_PATTERN.sub("\n", cell_) for cell_ in pad(row_)]
            for row_ in [header, *body]
        ],
        align=pad([_parse_align(cell_) for cell_ in delimiter]),
        aligned=all(
            _pipe_positions(line_) == first_positions for line_ in block_lines
        ),
    )


def _serialize_pipe_table(table: _PipeTable) -> List[str]:
    rows = [
        ["<br>".join(_cell_lines(cell_)).replace("|", "\\|") for cell_ in row_]
        for row_ in table.rows
    ]
    # Three characters fit the widest delimiter cell, ":-:".
    widths = [
        max([3] + [text_width(row_[column_]) for row_ in rows])
        for column_ in range(len(rows[0]))
    ]

    def render_row(cells: List[str]) -> str:
        return (
            "| "
            + " | ".join(
                cell_ + " " * (widths[column_] - text_width(cell_))
                for column_, cell_ in enumerate(cells)
            )
            + " |"
        )

    lines = [
        render_row(rows[0]),
        render_row(
            [
                _delimiter_cell(align_, widths[column_])
                for column_, align_ in enumerate(table.align)
            ]
        ),
        *(render_row(row_) for row_ in rows[1:]),
    ]
    return [table.indent + line_ for line_ in lines]


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _is_delimiter_row(line: str) -> bool:
    text = line.strip()
    return (
        _indent_width(line) < 4
        and DELIMITER_ROW_PATTERN.match(text) is not None
        and LIST_ITEM_DASH_PATTERN.match(text) is None
    )


def _is_table_row(line: str) -> bool:
    text = line.lstrip()
    return (
        text != ""
        and _indent_width(line) < 4
        and not any(pattern_.match(text) for pattern_ in BLOCK_START_PATTERNS)
    )


def _split_pipe_row(line: str) -> List[str]:
    r"""
    Split a row on unescaped "|" and unescape "\|" inside cells. The leading
    and trailing pipes are optional in GFM.
    """

    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]

    cells: List[str] = []
    cell = ""
    index = 0
    while index < len(text):
        if text[index] == "\\" and text[index + 1 : index + 2] == "|":
            cell += "|"
            index += 2
            continue
        if text[index] == "|":
            cells.append(cell.strip())
            cell = ""
        else:
            cell += text[index]
        index += 1
    cells.append(cell.strip())
    return cells


def _pipe_positions(line: str) -> List[int]:
    """
    Return the positions of the unescaped "|" in a line, measured in text
    width.
    """

    positions: List[int] = []
    index = 0
    while index < len(line):
        if line[index] == "\\" and line[index + 1 : index + 2] == "|":
            index += 2
            continue
        if line[index] == "|":
            positions.append(text_width(line[:index]))
        index += 1
    return positions


def _parse_align(cell: str) -> str:
    left = cell.startswith(":")
    right = cell.endswith(":")
    if left and right:
        return "center"
    if left:
        return "left"
    if right:
        return "right"
    return ""


def _delimiter_cell(align: str, width: int) -> str:
    if align == "left":
        return ":" + "-" * (width - 1)
    if align == "right":
        return "-" * (width - 1) + ":"
    if align == "center":
        return ":" + "-" * (width - 2) + ":"
    return "-" * width


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
