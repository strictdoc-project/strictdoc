# Table editor for multiline node fields

## WHAT

- The node form has a table editor for every multiline field with RST or
  Markdown markup. Fields with other markup, such as HTML or Text, have
  no table editor.
- Supported tables:
  - RST: grid tables without row or column spans and with at most one
    header row. A row can span several text lines, so a cell can hold
    several lines and paragraphs. The table can be indented (for
    example, under a `.. table::` directive).
  - Markdown: GFM pipe tables with the same number of cells in every
    row. A line break in a cell is `<br>` (`<br/>` and `<br />` are also
    read). Tables inside fenced code blocks are code, not tables.
- Recognition is live. A table-like block that does not match these rules
  has no highlight and no button, and the editor never rewrites it. After
  the user corrects the block by hand, it becomes editable.
- Editable tables in a field are highlighted. The table that holds the
  caret has a stronger highlight.
- While the field has focus, one button is shown in its left margin:
  - Edit: the caret is in an editable table. The button is next to the
    first line of the table and opens the table in the editor.
  - Insert: the caret is elsewhere. The button is next to the caret line
    and opens the editor with an empty table of 3 columns, a header row,
    and 2 body rows.
  - The button is hidden while the user types, while the caret is in an
    unrecognized table-like block, and when the field loses focus.
- Apply of a new table inserts it after the caret line, or in place of
  the caret line if that line is blank. Blank lines separate the table
  from the text around it.
- The editor is a modal with one multiline cell per table cell. Enter
  adds a line; a blank line separates paragraphs. Structure controls:
  - `+` buttons on the borders insert a row or a column.
  - Each column has a grip on the top border, and each body row has a
    grip on the left border. Dragging a grip moves the column or row.
    A click opens a menu: Insert above, Insert below, and Delete for a
    row; Insert left, Insert right, and Delete for a column.
  - Bars below and to the right of the table extend it. A click adds a
    row or a column at the end. Dragging adds rows or columns, or
    removes trailing empty ones; the drag stops at the first non-empty
    row or column.
  - The header row has no grip and cannot be moved or deleted. The
    table keeps at least one body row and one column.
- Apply writes the table into the field. Cancel or Escape closes the
  editor and leaves the field as it was. If a grip menu is open, Escape
  closes only the menu.
- The editor always shows a header row. On Apply:
  - RST: a header row with only empty cells is not written. The table
    has no header.
  - Markdown: a pipe table always has a header row; its cells can be
    empty.
- When the editor writes a table, it keeps:
  - the indent of the table;
  - a `|` inside an RST cell;
  - escaped `\|` inside a Markdown cell;
  - Markdown column alignment (the editor cannot change it).
- The editor realigns column widths to the longest cell line.
- Image upload into editor cells is not supported. Image markup typed as
  text in a cell works.

## WHY

Grid and pipe tables are tedious to edit as plain text. A change to one
cell often means realigning every border and row of the table by hand,
and a single misplaced `+` or `|` breaks the table.

Related requirement: SDOC-SRS-61 (Tables HTML editor).

## HOW

The editor is one client-side script with no server changes:
`table_editor.js` with `table_editor.css`, loaded only on the
server-mode document screen. Each format has a strict parser and a
serializer. The highlighting and the modal know nothing about the
format. The form validates the field text on save, as it does for text
typed by hand.

### Formats

`FORMATS` maps the form's `document_markup` value to a format object with
`findTables(lines)` and `serialize(table)`. Both formats share one table
model:

    { start, end, indent, hasHeader, rows, align }

`rows[0]` is the header row when `hasHeader` is true. A cell is a string;
`"\n"` separates its lines. `align` holds the Markdown column alignment
and is `null` for RST.

`findTables()` collects runs of candidate lines and passes each run to the
format's parser. It returns the accepted runs as tables and the rejected
runs of two or more lines as blocks. The parsers accept a run only when
they understand all of it. This check protects the source: the editor
serializes the whole table on Apply, so a misread table would be
corrupted.

- RST (`parseRstGridTable()`): the `+` positions of the top border define
  the column edges. Every border must have as many columns as the top
  border. A `=` border is allowed only after the first row. A row is the
  text lines between two borders. A row line still aligned with the top
  border is cut at the column edges, so a `|` elsewhere in it is cell
  text. A misaligned row line (after typing) is split on `|` and accepted
  only if that gives one part per column. Cell text is the parts joined
  by lines, without their common indent.
- Markdown (`parseMarkdownPipeTable()`): a header row, a delimiter row,
  and body rows, all with the same cell count. Rows split on unescaped
  `|`. Lines inside fenced code blocks are never candidates.

All lines of a table must share one indent. The serializer writes the
indent back.

### Field integration

- `StrictDoc.onInsert()` initializes every multiline contenteditable,
  including fields that Turbo inserts later. The script has no own
  `MutationObserver`.
- The button goes after the field's hidden textarea, because
  `editable_field.js` finds the textarea through
  `editable.nextElementSibling`. The button is absolutely positioned in
  `sdoc-form-field`, so it scrolls with the field.
- The source text is the field's `innerText`, the same value that
  `editable_field.js` saves.
- Apply replaces the field content with one text node and dispatches a
  bubbling `input` event. `editable_field.js` handles the event and
  updates the hidden textarea.
- Delegated `input`, `selectionchange`, `pointerup`, and `focusout`
  listeners on `document` rescan the field and update the highlights and
  the button. After `input`, the script records the caret position and
  keeps the button hidden until the caret moves elsewhere. The per-field
  state lives in a `Map`. The next highlight update drops the entries of
  fields that are no longer in the DOM.

### Highlighting

The highlights use the CSS Custom Highlight API (`::highlight(sdoc-table)`
and `::highlight(sdoc-table-active)`). The browser paints the text in
place, so there are no overlay elements to position on scroll or resize,
and nothing covers the text or blocks the caret.

The DOM-to-text mapping walks text nodes and `<br>` elements. If this
mapping does not match `innerText` (for example, when the field contains
other elements), the field gets no highlights and no edit button,
because the caret line cannot be computed reliably.

### Modal

The modal uses the existing `sdoc-backdrop` / `sdoc-modal` markup and is
appended to `#modal`. It carries `data-js-modal` and
`data-js-modal-cancel-button`, so `modal.js` handles Escape and Cancel.
While a grip menu is open, the backdrop stops the Escape event, so
`modal.js` does not close the modal. The modal edits a copy of the table.
The field changes only on Apply.

The cells are `sdoc-contenteditable` multiline fields without
`data-js-editable-field`, so `editable_field.js` does not handle them.
They have their own plain-text paste handler.

Grips and extend bars use pointer events with pointer capture, not HTML5
drag and drop. HTML5 drag and drop conflicts with text dragging in the
cells, and Selenium cannot drive it. A press that moves less than 4 px is
a click.

### Tests

The end-to-end test is
`tests/end2end/screens/document/table_editor/edit_and_insert_tables/`,
with one RST and one Markdown document. The page object is
`tests/end2end/helpers/components/table_editor.py` and uses test IDs.

- RST: the caret in a table with a span hides the button. A click on the
  extend bar adds a row; Cancel discards the new table. Typing in a table
  keeps it editable. The test edits a multi-line cell, inserts a column,
  and deletes a row through the grip menu. A drag on the extend bar of a
  new 3x3 table stops at a non-empty column.
- Markdown: in a fenced code block, the button inserts a new table. The
  test reads `\|` and `<br/>` in cells, writes a multi-line cell, inserts
  a row through the grip menu, inserts a column, and moves a column and a
  row by drag. The alignment moves with its column.
