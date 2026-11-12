# Table editor for multiline node fields

## WHAT

Multiline fields with RST or Markdown markup have a table editor. Fields
with other markup, such as HTML or Text, have no table editor. The editor
works in server mode on two screens: the document screen (node form) and
the table view (inline cell form).

### Supported tables

| Format | Table | Limits | Line break in a cell |
|---|---|---|---|
| RST | Grid table | No row or column spans. At most one header row. The table can have an indent, for example under a `.. table::` directive. | A row spans several text lines. A blank line separates paragraphs. |
| Markdown | GFM pipe table | Every row has the same number of cells. Tables inside fenced code blocks are code. | `<br>`. The editor also reads `<br/>` and `<br />`. |

Recognition is live. The editor never rewrites table-like text that does
not match these rules. Such text has no highlight and no edit button.
When the user corrects the text by hand, the table becomes editable.

### Field

The table editor is a field widget.
[Field widgets](../20261112_feat-field-widgets/task.md) describes the
field button and the insert menu.

The field highlights each editable table. The table that holds the caret
has a stronger highlight.

| Caret position | Field button | Click |
|---|---|---|
| In an editable table | Edit (`✎`), next to the first line of the table | Opens the table in the editor. |
| On a blank line | Insert (`+`) | The Table item of the insert menu opens the editor with an empty table of 3 columns, a header row, and 2 body rows. |

On Apply, a new table replaces the blank caret line. Blank lines separate
the table from the text around it.

### Editor

The editor is a modal with one multiline cell per table cell. Enter adds
a line. A blank line separates paragraphs.

Structure controls:

- `+` buttons on the borders insert a row or a column.
- Grips: each column has a grip on the top border. Each body row has a
  grip on the left border.
  - A drag moves the column or row.
  - A click opens a menu. Row menu: Insert above, Insert below, Delete.
    Column menu: Insert left, Insert right, Delete.
- Extend bars below and to the right of the table:
  - A click adds a row or a column at the end.
  - A drag adds rows or columns, or removes trailing empty ones. The drag
    stops at the first non-empty row or column.

The header row has no grip. The user cannot move or delete the header
row. The table keeps at least one body row and one column.

Apply writes the table into the field. Cancel or Escape closes the editor,
and the field stays as it was. If a grip menu is open, Escape closes only
the menu.

The editor always shows a header row. On Apply:

- RST: if all header cells are empty, the editor writes the table without
  a header.
- Markdown: a pipe table always has a header row. The header cells can be
  empty.

When the editor writes a table, the editor:

- keeps the table indent
- keeps a `|` inside an RST cell
- keeps an escaped `\|` inside a Markdown cell
- keeps the Markdown column alignment (the editor cannot change the alignment)
- realigns the column widths to the longest cell line.

The editor cells do not support image upload. Image markup typed as text
in a cell works.

## WHY

Grid and pipe tables are tedious to edit as plain text. A change to one
cell often means a manual realignment of every border and row of the
table. A single misplaced `+` or `|` breaks the table.

Related requirement: SDOC-SRS-61 (Tables HTML editor).

## HOW

The editor is a client-side script, `table_editor.js`, with
`table_editor.css`. The script is the `table` widget of
`field_widgets.js`. The screens load both files in server mode only. Each
format has a strict parser and a serializer. The highlights and the modal
do not depend on the format. On save, the form validates the field text,
the same as text typed by hand.

### Formats

`FORMATS` maps the `document_markup` value of the form to a format object
with `findTables(lines)` and `serialize(table)`. Both formats use one
table model:

    { start, end, indent, hasHeader, rows, align }

- `rows[0]` is the header row when `hasHeader` is true.
- A cell is a string. `"\n"` separates the lines of a cell.
- `align` holds the Markdown column alignment. For RST, `align` is `null`.

`findTables()` collects runs of candidate lines and sends each run to the
format parser. `findTables()` returns the runs that the parser accepts as
tables. The parser accepts a run only if the parser understands the whole
run. This strict check protects the source: on Apply, the editor
serializes the whole table and would corrupt a misread table.

RST (`parseRstGridTable()`):

- The `+` positions of the top border define the column edges.
- Every border has as many columns as the top border.
- A `=` border can follow only the first row.
- A row is the text lines between two borders.
- A row line that is still aligned with the top border is cut at the
  column edges. As a result, a `|` elsewhere in the line is cell text.
- A misaligned row line (after typing) is split on `|`. The parser accepts
  the line only if the split gives one part per column.
- Cell text is the parts joined by lines, without their common indent.

Markdown (`parseMarkdownPipeTable()`):

- A table is a header row, a delimiter row, and body rows.
- All rows have the same cell count.
- Rows split on unescaped `|`.
- Lines inside fenced code blocks are never candidates.

All lines of a table must have one indent. The serializer writes the
indent back.

### Widget

The table widget implements the widget contract of `field_widgets.js`:

- `supports()` accepts the markups in `FORMATS`.
- `scan()` finds the tables of the field and updates the highlights.
- `blockAt()` returns the table that holds a line.
- `activate()` sets the stronger highlight on the table that holds the
  caret.
- `edit()` and `insert()` open the modal. On Apply, the widget writes the
  table with `replaceLines()` or `insertBlock()`.

A `Map` holds the tables of each field. The next highlight update removes
the entries of the fields that are no longer in the DOM.

### Highlighting

The highlights use the CSS Custom Highlight API
(`::highlight(sdoc-table)` and `::highlight(sdoc-table-active)`). The
browser paints the text in place. As a result, no overlay elements need
a new position on scroll or resize. Nothing covers the text or blocks
the caret.

If `field_widgets.js` cannot map the field DOM to its text, `lineRange()`
returns null. In this case, the field has no table highlights.

### Modal

The modal uses the existing `sdoc-backdrop` / `sdoc-modal` markup and goes
into `#modal`. The modal has `data-js-modal` and
`data-js-modal-cancel-button`, so `modal.js` handles Escape and Cancel.
While a grip menu is open, the backdrop stops the Escape event, so
`modal.js` does not close the modal. The modal edits a copy of the table.
The field changes only on Apply.

In the table view, `table_view_edit.js` saves the cell on an outside
click and cancels the cell on Escape. The modal is outside the cell, so
`table_view_edit.js` ignores events with a `[data-js-modal]` element in
`composedPath()`. `modal.js` runs first and can remove the modal, but the
event path still lists the modal. The backdrop is focusable (`tabIndex`
-1), so a click on a non-focusable part of the modal keeps the focus in
the modal.

The cells are `sdoc-contenteditable` multiline fields without
`data-js-editable-field`, so `editable_field.js` does not handle the
cells. The cells have their own plain-text paste handler.

Grips and extend bars use pointer events with pointer capture. HTML5 drag
and drop conflicts with text drag in the cells, and Selenium cannot drive
HTML5 drag and drop. A press that moves less than 4 px is a click.

### Tests

The page object is `tests/end2end/helpers/components/table_editor.py`. The
page object uses test IDs.

`tests/end2end/screens/document/table_editor/edit_and_insert_tables/` has
one RST document and one Markdown document.

- RST: the caret in a table with a span or at the end of a text line hides
  the button. Escape closes the insert menu, and the form stays open. A
  click on the extend bar adds a row. Cancel discards the new table.
  Typing in a table keeps the table editable. The test edits a multi-line
  cell, inserts a column, and deletes a row through the grip menu. A drag
  on the extend bar of a new 3x3 table stops at a non-empty column.
- Markdown: the test reads `\|` and `<br/>` in cells and writes a
  multi-line cell. The test inserts a row through the grip menu, inserts a
  column, and moves a column and a row by drag. The alignment moves with
  its column.

`tests/end2end/screens/table/view_table_edit/edit_table_cell_statement_table_editor/`
covers the table view:

Escape in the editor closes only the editor, and the cell stays in edit
mode. Clicks in the editor do not save the cell. Apply writes the table
into the cell. An outside click saves the cell.
