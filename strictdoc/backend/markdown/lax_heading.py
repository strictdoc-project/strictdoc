"""
ATX heading rule without the CommonMark six-``#`` cap.

CommonMark stops recognizing ATX headings at six ``#`` characters, while
StrictDoc documents support arbitrary section nesting. Following the
precedent of Pandoc's Markdown reader, this rule accepts any number of
``#`` characters so that documents nested deeper than six levels survive
the SDoc -> Markdown -> SDoc round-trip. All other CommonMark heading
conventions are preserved: the hashes must be followed by a space, a tab,
or the end of the line; an optional closing hash sequence is trimmed; and
indented code blocks are excluded.

The implementation mirrors ``markdown_it.rules_block.heading`` with the
level cap removed.
"""

from markdown_it import MarkdownIt
from markdown_it.common.utils import isStrSpace
from markdown_it.rules_block.state_block import StateBlock


def lax_heading(
    state: StateBlock,
    startLine: int,
    endLine: int,  # noqa: ARG001
    silent: bool,
) -> bool:
    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]

    if state.is_code_block(startLine):
        return False

    ch = state.src[pos] if pos < maximum else None

    if ch != "#" or pos >= maximum:
        return False

    # Count the heading level without the CommonMark <= 6 cap.
    level = 1
    pos += 1
    ch = state.src[pos] if pos < len(state.src) else None
    while ch == "#" and pos < maximum:
        level += 1
        pos += 1
        ch = state.src[pos] if pos < len(state.src) else None

    if pos < maximum and not isStrSpace(ch):
        return False

    if silent:
        return True

    # Cut tails like '    ###  ' from the end of the heading line.
    maximum = state.skipSpacesBack(maximum, pos)
    tmp = state.skipCharsStrBack(maximum, "#", pos)
    if tmp > pos and isStrSpace(state.src[tmp - 1]):
        maximum = tmp

    state.line = startLine + 1

    token = state.push("heading_open", "h" + str(level), 1)
    token.markup = "#" * level
    token.map = [startLine, state.line]

    token = state.push("inline", "", 0)
    token.content = state.src[pos:maximum].strip()
    token.map = [startLine, state.line]
    token.children = []

    token = state.push("heading_close", "h" + str(level), -1)
    token.markup = "#" * level

    return True


def create_lax_heading_markdown_parser() -> MarkdownIt:
    """Create the CommonMark parser used by the reader, with deep headings."""
    markdown_parser = MarkdownIt("commonmark")
    markdown_parser.block.ruler.at("heading", lax_heading)
    return markdown_parser
