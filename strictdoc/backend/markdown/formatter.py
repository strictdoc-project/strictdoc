"""
Formatter for Markdown content in SDoc TEXT nodes and .md files.
Wraps long prose paragraphs and list items to a configurable line width while
preserving Markdown structure (headings, fenced code, tables, blockquotes, etc.).
"""

import re
import textwrap
from typing import List

from strictdoc.helpers.string import _protect_inline, _restore_inline

# Markdown list item markers (task lists matched first — more specific)
#   group 1: leading whitespace
#   group 2: marker including trailing space(s)
#   group 3: content
_MD_LIST_ITEM_RE = re.compile(
    r"^(\s*)"
    r"([-*+] \[[ xX]\] |[-*+] |\d+[.)]\s+)"
    r"(.+)$"
)

# Lines that signal content that must not be reflowed
_MD_PRESERVE_LINE_RE = re.compile(
    r"^("
    r"\s"  # indented block (code, continuation, blockquote)
    r"|#{1,6} "  # ATX heading
    r"|`{3}"  # fenced code block
    r"|~{3}"  # fenced code block (tilde)
    r"|>"  # blockquote
    r"|\|"  # table cell
    r"|\+[-=]"  # table border
    r"|-{3,}"  # setext heading underline or thematic break
    r"|={3,}"  # setext heading underline
    r"|\*{3,}"  # thematic break
    r")"
)


def wrap_md_text(text: str, line_width: int) -> str:
    """Wrap Markdown text to *line_width* columns, preserving Markdown structure."""
    paragraphs = re.split(r"(\n{2,})", text)
    result: List[str] = []
    for chunk in paragraphs:
        if re.fullmatch(r"\n{2,}", chunk):
            result.append(chunk)
            continue
        result.append(_wrap_chunk(chunk, line_width))
    return "".join(result)


def _wrap_chunk(chunk: str, line_width: int) -> str:
    lines = chunk.split("\n")
    non_empty = [line for line in lines if line]

    # Already within width — nothing to do.
    if all(len(line) <= line_width for line in lines):
        return chunk

    # Blocks containing preserved lines — keep as-is.
    if any(_MD_PRESERVE_LINE_RE.match(line) for line in non_empty):
        return chunk

    # Pure list block — wrap each item individually with correct continuation.
    if non_empty and all(_MD_LIST_ITEM_RE.match(line) for line in non_empty):
        return _wrap_list_block(lines, line_width)

    # Plain prose paragraph.
    return _wrap_plain(chunk, line_width)


def _wrap_list_block(lines: List[str], line_width: int) -> str:
    result = []
    for line in lines:
        if not line or len(line) <= line_width:
            result.append(line)
            continue
        m = _MD_LIST_ITEM_RE.match(line)
        if m:
            result.append(_wrap_list_item(line, m, line_width))
        else:
            result.append(line)
    return "\n".join(result)


def _wrap_list_item(line: str, m: "re.Match[str]", line_width: int) -> str:
    leading = m.group(1)  # leading whitespace (nesting indent)
    marker = m.group(2)  # marker including trailing space(s)
    subsequent = leading + " " * len(marker)

    protected = _protect_inline(line)
    content_tokens = protected[len(leading) + len(marker) :].split()

    # Exception: if the first content token is an inline link or keyword
    # (detected by the presence of the \x00 placeholder used during
    # protection), keep it on the same line as the list marker even if the
    # resulting line exceeds line_width.
    if content_tokens and "\x00" in content_tokens[0]:
        first_line = leading + marker + _restore_inline(content_tokens[0])
        if len(content_tokens) == 1:
            return first_line
        remaining_wrapped = textwrap.fill(
            " ".join(content_tokens[1:]),
            width=line_width,
            initial_indent=subsequent,
            subsequent_indent=subsequent,
            break_on_hyphens=False,
            break_long_words=False,
        )
        return first_line + "\n" + _restore_inline(remaining_wrapped)

    # Normal path: let textwrap reflow with continuation indentation.
    wrapped = textwrap.fill(
        protected,
        width=line_width,
        subsequent_indent=subsequent,
        break_on_hyphens=False,
        break_long_words=False,
    )
    return _restore_inline(wrapped)


def _wrap_plain(chunk: str, line_width: int) -> str:
    protected = _protect_inline(chunk)
    wrapped = textwrap.fill(
        protected,
        width=line_width,
        break_on_hyphens=False,
        break_long_words=False,
    )
    return _restore_inline(wrapped)
