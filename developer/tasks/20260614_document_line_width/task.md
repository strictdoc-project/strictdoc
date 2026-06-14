# Add an option to enable fixed-width content formatting for SDoc and Markdown documents

## WHAT

Add optional fixed-width content formatting for SDoc and Markdown documents.

Introduce a config option `document_line_width` to the project configuration.
When enabled, this option should make the SDoc and Markdown writers format
document content to the given line width limit.

In particular, when the `document_line_width` is set, editing of all nodes in
the web interface and writing them back to file system, shall respect the given
line width limit.

Introduce `strictdoc format` command that acts like `black` or `ruff`, reading
the input documents and outputting the line width-formatted content back
(in-place editing for now).

The minimal acceptable limit shall be `80`.

The user manual shall be updated to reflect the new `format` command.

The formatters for Markdown and RST shall be implemented in separate dedicated Python files. Rationale: Easier maintainance of two similar but different markups.

The formatting shall not affect the long code blocks inside backticks of
Markdown and `.. code::` sections of RST.

The formatting shall treat the StrictDoc `[LINK: ]` and `[ANCHOR: ]` keywords
as full words, never splitting them in parts.

The formatting shall treat Markdown and RST links as full words. If such a link causes a given line to exceed its limit, the link shall be written as a single word on a separate line.

Add a dedicated integration smoke test that runs the `format` against the
StrictDoc documentation in `docs/` twice. This is to ensure that the
formatting always works against StrictDoc's own documentation.

Formatting shall both respect and modify the bullet or numbered lists in the following way:

- Left indentation before the list keywords such as `- ` or `* ` must be always respected.
- The lines starting 

## WHY

The automatic formatting helps to avoid the manual effort of re-formatting
documents when a user wants to have their content to have fixed line width.

## HOW

### Implementation details

When running `format`, StrictDoc shall only build a traceability index for
documents and avoid reading source files. This is to run the command faster
because the source file information is not required for correct formatting
of documents.

### Extra spec items

### General

* The formatter wraps text lines to a configurable maximum width.
* The default maximum width is 80 characters.
* The formatter preserves the input document format:

  * Markdown remains valid Markdown.
  * reStructuredText remains valid reStructuredText.
* The formatter does not alter the semantic content of the document.
* The formatter preserves blank lines.
* The formatter preserves indentation-sensitive document structure.

### Markdown lists

* The formatter preserves unordered Markdown list markers:

  * `-`
  * `*`
  * `+`
* The formatter preserves ordered Markdown list markers:

  * `1.`
  * `2.`
  * `1)`
  * Similar valid Markdown numbering styles.
* The formatter preserves the indentation of nested Markdown lists.
* Wrapped continuation lines align with the content of the list item rather than with the list marker.

Example:

```markdown
- This is a long list item that wraps onto
  the next line.
```

* The formatter does not renumber ordered lists.
* The formatter preserves task list syntax such as:

  * `- [ ]`
  * `- [x]`
* Wrapped continuation lines in task lists align with the content following the checkbox marker.

### reStructuredText lists

* The formatter preserves unordered list markers:

  * `-`
  * `*`
  * `+`
* The formatter preserves enumerated list markers:

  * `1.`
  * `A.`
  * `a.`
  * `I.`
  * `i.`
  * `#.`
* The formatter preserves nested list indentation.
* Wrapped continuation lines align with the list item content.
* The formatter preserves definition lists.
* The formatter preserves field lists such as:

```rst
:field: value
```

### Line wrapping

* The formatter wraps prose without exceeding the configured width whenever possible.
* The formatter does not split words.
* The formatter treats Markdown inline links as atomic tokens.

Example:

```markdown
[link text](https://example.com/very/long/url)
```

* The formatter treats reStructuredText inline links as atomic tokens.

Example:

```rst
`link text <https://example.com/very/long/url>`_
```

* If a Markdown or reStructuredText link would cause a line to exceed the configured width, the entire link is moved to a separate line.
* Exception: If the link is the first content of a list item, the formatter shall keep the link on the same line as the list marker, even if the resulting line exceeds the configured width.
* The formatter may allow an individual atomic token to exceed the configured width if splitting it would invalidate syntax or alter semantics.
* The formatter does not insert whitespace inside link syntax.
* The formatter treats inline code spans as atomic tokens.
* The formatter does not wrap inside Markdown autolinks or RST code blocks:

```markdown
<https://example.com>
```

* The formatter does not wrap inside bare URLs unless explicitly configured to do so.

### List-specific wrapping rules

* The formatter preserves the list marker and its associated content as a single logical list item.
* Wrapped lines remain visually associated with their parent list item.
* Nested list items preserve their relative indentation after wrapping.
* A wrapped line must never be interpreted as a sibling list item when parsed by Markdown or reStructuredText.
* Wrapping must not alter list nesting depth.
* Wrapping must not convert a list item into a paragraph or vice versa.
* A list item containing only a long link may be rendered as:

```markdown
-
  [very long link](...)
```

or

```markdown
- [very long link](...)
```

provided that the resulting syntax remains valid and unambiguous.

* The formatter preserves blank lines that are semantically significant within list structures.

### Blocks that must not be rewrapped

* The formatter does not rewrap fenced Markdown code blocks.
* The formatter does not rewrap indented Markdown code blocks.
* The formatter does not rewrap reStructuredText literal blocks introduced by `::`.
* The formatter does not rewrap reStructuredText code blocks introduced by directives such as:

```rst
.. code-block::
```

* The formatter does not rewrap tables unless table formatting support is explicitly enabled.
* The formatter does not modify directive structure.

### Inline markup preservation

* The formatter preserves Markdown emphasis syntax:

  * `*text*`
  * `_text_`
  * `**text**`
  * `__text__`
* The formatter preserves Markdown inline code syntax.
* The formatter preserves Markdown image syntax.
* The formatter preserves reStructuredText emphasis, strong emphasis, interpreted text, substitutions, and inline literals.
* The formatter preserves reStructuredText reference syntax, including:

  * `reference_`
  * `anonymous__`
  * `` `phrase reference`_ ``
* The formatter preserves Markdown reference-style links.
* The formatter preserves reStructuredText hyperlink targets.

### Idempotency and stability

* Formatting an already formatted document produces identical output.
* Formatting is deterministic.
* The formatter does not introduce trailing whitespace.
* Final newline handling is configurable.

### Error handling

* When malformed Markdown or reStructuredText is encountered, the formatter avoids destructive transformations.
* When syntax cannot be parsed with confidence, the formatter applies conservative formatting behavior.
* Optional diagnostics may report formatting limitations and ambiguities.

### Configuration

* The maximum line width is configurable.
* Markdown-specific behavior is configurable independently from reStructuredText-specific behavior.
* Individual block types may be excluded from wrapping.
* Existing manual line breaks may optionally be preserved.
* List indentation normalization may optionally be enabled.

### Testing

* Tests cover flat Markdown unordered lists.
* Tests cover nested Markdown unordered lists.
* Tests cover Markdown ordered lists.
* Tests cover Markdown task lists.
* Tests cover flat reStructuredText bullet lists.
* Tests cover nested reStructuredText bullet lists.
* Tests cover reStructuredText enumerated lists.
* Tests cover links that fit within the configured width.
* Tests cover links that exceed the configured width.
* Tests cover cases where a link must occupy its own line.
* Tests verify that code blocks, literal blocks, directives, and tables are not corrupted by formatting.
