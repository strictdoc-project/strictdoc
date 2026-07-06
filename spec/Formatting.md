# Formatting specification

**Grammar**: Markdown.gra.md

This specification defines the behavior of StrictDoc's text formatter for
Markdown and reStructuredText (RST) content. The formatter wraps long lines to
a configurable maximum width while preserving document structure and semantics.

The formatter is implemented in two separate modules:
`strictdoc/backend/rst/formatter.py` for RST content in SDoc TEXT nodes and
`strictdoc/backend/markdown/formatter.py` for Markdown content in SDoc TEXT
nodes and standalone `.md` files.

## General behavior

### Line width

**MID**: f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6 \
**UID**: FMT-1

**Statement**: The formatter wraps text lines to a configurable maximum line
width. The minimum acceptable line width is 80 characters.

### Prose wrapping

**MID**: a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7 \
**UID**: FMT-2

**Statement**: The formatter wraps plain prose paragraphs so that no output
line exceeds the configured line width. Paragraph boundaries (two or more
consecutive blank lines) are preserved. The formatter does not split individual
words.

### Blank lines

**MID**: b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8 \
**UID**: FMT-3

**Statement**: The formatter preserves blank lines that separate paragraphs or
list items. No blank lines are added or removed during formatting.

### Idempotency

**MID**: c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9 \
**UID**: FMT-4

**Statement**: Formatting an already-formatted document produces identical
output. Running the formatter twice on the same input produces the same result
as running it once.

### No semantic change

**MID**: d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0 \
**UID**: FMT-5

**Statement**: The formatter does not alter the semantic content of the
document. It only changes line-break positions within wrappable prose.

### Blocks that must not be rewrapped

**MID**: e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1 \
**UID**: FMT-6

**Statement**:

The formatter preserves the following block types unchanged,
regardless of line length:

- Fenced code blocks (Markdown ` ``` ` or `~~~`, and analogous RST forms).
- Indented blocks (any leading whitespace signals code, continuation, or a
  blockquote and is left untouched).
- reStructuredText directives (`.. name::`).
- reStructuredText literal blocks introduced by `::`.
- reStructuredText field lists (`:field: value`).
- Tables (Markdown pipe tables and RST grid/simple tables).
- Blockquotes (`>`).

### Inline links as atomic tokens

**MID**: f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2 \
**UID**: FMT-7

**Statement**:

The formatter treats inline links as atomic tokens that are
never broken across lines:

- Markdown inline links: `[text](url)`
- reStructuredText hyperlinks: `` `text <url>`_ `` and `` `text <url>`__ ``

If an atomic token would cause the current line to exceed the configured width,
the entire token is moved to the next line as a single unit.

The formatter may allow a single atomic token to exceed the configured width
when no line-break position within the token exists.

## Markdown formatting

### Markdown list markers

**MID**: 08b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3 \
**UID**: FMT-MD-1

**Statement**:

The formatter recognises and preserves the following unordered
Markdown list markers: `-`, `*`, `+`. The following ordered list markers are
also recognised: digit-based styles such as `1.`, `2.`, `1)`.

Task list markers (`- [ ]`, `- [x]`, `- [X]`) are also recognised and
preserved.

### Markdown list continuation indentation

**MID**: 19c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4 \
**UID**: FMT-MD-2

**Statement**:

When a Markdown list item is wrapped, continuation lines are
indented to align with the content of the list item, not with the list marker.

Example:

```markdown
- This is a long list item that wraps onto
  the next line.
```

The continuation indent equals the total width of the leading whitespace plus
the marker (including its trailing space). For a `- ` marker the indent is
2 spaces; for a `1. ` marker it is 3 spaces; for a `- [ ] ` task marker it is
6 spaces.

### Markdown preserved blocks

**MID**: 2ad1e2f3a4b5c6d7e8f9a0b1c2d3e4f5 \
**UID**: FMT-MD-3

**Statement**:

The formatter does not rewrap the following Markdown constructs:

- ATX headings (lines starting with one to six `#` characters).
- Fenced code blocks (content between ` ``` ` or `~~~` fence lines).
- Indented code blocks (4 or more leading spaces).
- Blockquotes (lines starting with `>`).
- Pipe table rows and column-separator lines.
- Thematic breaks (`---`, `===`, `***`).

## reStructuredText formatting

### RST list markers

**MID**: 3be2f3a4b5c6d7e8f9a0b1c2d3e4f5a6 \
**UID**: FMT-RST-1

**Statement**:

The formatter recognises and preserves the following RST list
markers:

- Unordered: `-`, `*`, `+`.
- Enumerated: arabic numerals (`1.`, `2.`), uppercase and lowercase letters
  (`A.`, `a.`), uppercase and lowercase Roman numerals (`I.`, `i.`), and
  auto-number (`#.`). Both period (`.`) and right-parenthesis (`)`) suffixes
  are recognised.

### RST list continuation indentation

**MID**: 4cf3a4b5c6d7e8f9a0b1c2d3e4f5a6b7 \
**UID**: FMT-RST-2

**Statement**:

When an RST list item is wrapped, continuation lines are
indented to align with the content of the list item, not with the list marker.

Example:

```rst
- This is a long list item that wraps onto
  the next line.

1. A numbered item that wraps onto
   the next line.
```

The continuation indent equals the total width of the leading whitespace plus
the marker (including its trailing space).

### RST preserved blocks

**MID**: 5da4b5c6d7e8f9a0b1c2d3e4f5a6b7c8 \
**UID**: FMT-RST-3

**Statement**:

The formatter does not rewrap the following RST constructs:

- Any line with leading whitespace (indented code, continuation lines, or
  nested content).
- RST directives (lines starting with `.. `).
- RST literal block markers (`::` standalone or at line end).
- RST field lists (lines starting with `:letter`).
- RST table cells (`|`) and table borders (`+---`, `+===`).
- Blockquotes (`>`).

## StrictDoc-specific rules

### LINK keyword as atomic token

**MID**: 6eb5c6d7e8f9a0b1c2d3e4f5a6b7c8d9 \
**UID**: FMT-SD-1

**Statement**: The formatter treats `[LINK: uid]` as an atomic token. The
space between the colon and the UID is not a valid line-break position. If the
keyword would cause the current line to exceed the configured width, the entire
`[LINK: uid]` expression is moved to the next line as a single unit.

### ANCHOR keyword as atomic token

**MID**: 7fc6d7e8f9a0b1c2d3e4f5a6b7c8d9e0 \
**UID**: FMT-SD-2

**Statement**: The formatter treats `[ANCHOR: uid]` as an atomic token with
the same line-break rules as FMT-SD-1.

### Link as first content of a list item

**MID**: 80d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1 \
**UID**: FMT-SD-3

**Statement**:

If an inline link or a StrictDoc cross-reference keyword
(`[LINK: uid]` or `[ANCHOR: uid]`) is the first content of a list item —
immediately following the list marker with no preceding prose — the formatter
keeps the token on the same line as the list marker, even if the resulting line
exceeds the configured width.

This rule applies to both Markdown and RST list items and takes precedence over
FMT-7.

Example (RST):

```rst
- `Very long link text <https://example.com/a/very/long/path/to/a/resource>`_
  followed by more prose on the continuation line.
```
