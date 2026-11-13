# Field widgets

## WHAT

Multiline fields have widgets that insert and edit markup elements. The
widgets work in server mode on two screens: the document screen (node
form) and the table view (inline cell form).

| Widget | Markup | Description |
|---|---|---|
| Table | RST, Markdown | [Table editor](../20261109_feat_table_editor/task.md) |
| Link | RST, Markdown | [Link widget](#link-widget) |
| Anchor | RST, Markdown | [Anchor widget](#anchor-widget) |

The widgets work only with RST and Markdown.

### Field button

While the field has focus, one button shows in the left margin of the
field:

| Caret position | Button | Location | Click |
|---|---|---|---|
| In a block that a widget can edit | Edit (`✎`) | Next to the first line of the block | Opens the widget editor for the block. |
| On a blank line outside such a block | Insert (`+`) | Next to the caret line | Opens the insert menu. |

The button hides on any other caret line, while the user types, and when
the field loses focus. The insert button shows only if a widget supports
the field markup.

### Insert menu

The insert menu has one item for each widget that supports the field
markup. An item inserts a new element at the blank caret line. The menu
opens under the button, or above the button if there is no room below.

The menu closes:

- on a second click on the button
- on Escape
- on a click outside the menu
- when the caret moves to another line.

Escape closes only the menu. In the table view, the cell stays in edit
mode.

### Link widget

The link widget writes a `[LINK: <UID>]` tag without a link title. A list
of link targets opens at the caret. The targets are the documents,
sections, nodes, and anchors with a UID. The targets of the current
document come first.

The list opens on these triggers:

| Trigger | Query | The tag replaces |
|---|---|---|
| `@` at the start of a word | The text after `@`, up to the caret | `@` and the query |
| `[LINK:` | The text after `[LINK:`, up to the caret | `[LINK:` and the query |
| Link item of the insert menu | The text typed after the item writes `@` on the blank caret line | `@` and the query |

The list behavior:

- A query can have several words. A target matches if its UID and title
  together contain every word.
- After `@`, a space can start plain text, for example `meet @ 10:00`.
  As a result, a query with a space that matches no target closes the
  list. A query without a space that matches no target shows "No matches
  found".
- Only typing opens the list. A caret move only closes the list, when the
  caret leaves the trigger. As a result, a click into old text with `@`,
  such as an e-mail address, does not open the list.
- The list stays hidden until the first response arrives. While the list
  is hidden, the keys work as usual.
- The arrow keys move the selection. Enter or Tab writes the selected
  target. A click on a target writes the target.
- Escape closes only the list and keeps the typed text. In the table view,
  the cell stays in edit mode.
- After Escape, or after a query with a space that matches no target, the
  list stays closed until the user starts another trigger.

### Anchor widget

The anchor widget writes an `[ANCHOR: <UID>]` or `[ANCHOR: <UID>, <title>]`
tag on the blank caret line. An anchor tag is block-level, and the insert
button shows only on a blank line. The widget does not edit existing
anchors.

The Anchor item of the insert menu opens a form under the field button:

| Input | Required | Check while the user types |
|---|---|---|
| UID | yes | The UID follows the UID syntax of the SDoc grammar. No document, node, or saved anchor in the project has this UID. No anchor in the field text has this UID, including the anchors that are not saved yet. |
| Title | no | The tag syntax can hold the title (see below). |

- The Insert button works only when both inputs pass the checks. A message under
  the input names the problem, for example the kind of the target that
  already has the UID.
- A title with `,` or `]` goes in double quotes. Such a title cannot
  contain a double quote. A title without `,` and `]` cannot start or end
  with a double quote, because the parser removes the quotes at the ends.
- Enter in an input inserts the anchor. Escape or Cancel closes the form.
  Both give the focus back to the field. A click outside the form closes
  the form.
- In the table view, the clicks and keys in the form do not save or cancel
  the edited cell.

The checks of the form help the user. The server still validates the
anchors when the user saves the node form.

## WHY

Markup elements such as tables and links have a strict syntax. A user must
remember the syntax and type every element by hand. One typing error
breaks the element. A link also needs the exact UID of its target, which
the user must look up in another document or screen. A new anchor needs a
UID that no other target uses, and the user learns about a conflict only
when the user saves the node form.

Related requirement: SDOC-SRS-208 (Field widgets).

## HOW

`field_widgets.js` with `field_widgets.css` holds the parts that all
widgets share: the field text, the button, the insert menu, and the write
back into the field. Each widget is a separate script that registers with
`StrictDoc.fieldWidgets.register()`. The screens load `field_widgets.js`
before the widget scripts, in server mode only.

### Widget contract

A widget is an object with these members:

| Member | Required | Purpose |
|---|---|---|
| `id` | yes | Name of the insert menu item, its test ID, and its icon in `components/field_widgets/icons.jinja`. |
| `label` | yes | Text of the insert menu item. |
| `supports(markup)` | yes | True if the widget works with the markup. |
| `insert(field, line, rect)` | yes | Inserts a new element at the blank caret line. `rect` is the viewport rectangle of the field button, for a widget that shows its own popup there. |
| `scan(field, lines, markup)` | no | Called after every change of the text of a field with a supported markup. |
| `forget(field)` | no | Called when the field is no longer in the DOM. The widget drops its data about the field. |
| `blockAt(field, line)` | no | Returns the block `{start, end, ...}` that holds the line, or null. |
| `editTitle` | no | Title of the edit button. |
| `edit(field, block)` | no | Edits a block from `blockAt()`. |
| `activate(field, block)` | no | Called on every caret move with the block that holds the caret, or null. |

Any widget can have `scan()` and `forget()`. The members from `blockAt()`
to `activate()` are for widgets that recognize their own blocks in the
field text, such as tables.

`StrictDoc.fieldWidgets` also gives the widgets seven helpers:

- `hasWidget(field, id)`: true if the widget works in the field.
- `lineRange(field, start, end)`: a DOM range for the lines, or null if
  the script cannot map the field DOM to its text.
- `textBeforeCaret(field)`: the field text before the caret, or null if
  the caret is not in the field or the script cannot map the field DOM to
  its text.
- `insertBlock(field, line, blockLines)`: writes the lines in place of the
  blank caret line. Blank lines separate the block from the text around
  it.
- `replaceLines(field, start, end, newLines)`: writes the lines in place of
  the lines from `start` to `end`.
- `replaceText(field, from, to, text)`: writes the text in place of the
  characters from `from` to `to` and puts the caret after the text.
- `placeFixed(element, rect)`: puts a fixed element under the rectangle,
  or above it if there is no room below, inside the viewport.

A widget popup that the form must not cut goes into `<body>` with a fixed
position. Inside the form, the overflow of `sdoc-form-grid` would cut the
popup: `sdoc-node` is a CSS container, and a container is the containing
block of its fixed descendants. In the table view, a click or a key
outside the edited cell saves or cancels the cell. As a result, such a
popup stops the propagation of its clicks and keys.

A widget script can load after `field_widgets.js` initializes the fields.
As a result, `register()` scans the fields that already exist.

### Field integration

- `StrictDoc.onInsert()` initializes every multiline contenteditable,
  including the fields that Turbo inserts later. The script has no
  `MutationObserver` of its own.
- The field markup comes from the `document_markup` input of the form.
  The table view cell form gets this input from the
  `table__get_node_contenteditable_inline` route.
- The button goes after the hidden textarea of the field, because
  `editable_field.js` finds the textarea through
  `editable.nextElementSibling`. The button is absolutely positioned in
  `sdoc-form-field`, so the button scrolls with the field.
- The insert menu is a fixed popup in `<body>` (see the helpers), placed
  with `placeFixed()` at the button. The menu stops the propagation of
  its clicks and follows the button on scroll and on a window resize.
- The source text is the `innerText` of the field, the same value that
  `editable_field.js` saves.
- A write replaces the field content with one text node and dispatches a
  bubbling `input` event. `editable_field.js` handles the event and
  updates the hidden textarea.
- Delegated `input`, `selectionchange`, `pointerup`, and `focusout`
  listeners on `document` rescan the field and update the button. After
  `input`, the script records the caret position. The button stays hidden
  until the caret moves elsewhere.
- A `Map` holds the state of each field. A rescan removes the entries of
  the fields that are no longer in the DOM and calls `forget()` of every
  widget for each removed field.
- In the table view, Escape in a field cancels the cell edit. When the
  insert menu is open, a capture listener on `document` stops the Escape
  event and closes only the menu.

### Link widget implementation

`link_widget.js` with `link_widget.css` is the `link` widget. The widget
has no blocks of its own. As a result, the widget implements only
`supports()` and `insert()`. The widget listens to `input` itself and
checks the field with `hasWidget()`.

The list of link targets comes from `GET /autocomplete/link`:

- `q` is the query. A target matches if its UID and title together
  contain every word of the query, case-insensitive. An empty `q` matches
  every target. Without `q`, the response is empty.
- The target whose UID equals `q` (case-sensitive, without the spaces
  around `q`) comes first. The index finds it directly, so the limit of
  the list cannot cut it. The anchor widget uses this item to check if a
  UID is taken.
- `document_mid` is optional. The targets of this document come first.
  The widget sends the `context_document_mid` input of the form, that is,
  the document on the screen. The table view cell form gets this input
  from the `table__get_node_contenteditable_inline` route.
- The server walks the traceability index: each document, then the nodes
  of the document in tree order, then the anchors in the node fields. The
  response has at most `AUTOCOMPLETE_LIMIT` (50) targets.
- Each response item has the same markup as the `/autocomplete/uid` items
  and a kind label. The label of a node is its grammar element tag, such
  as `SECTION`, `REQUIREMENT`, or `TEST_CASE`, the same text that the UI
  shows elsewhere. A grammar element has no other name. The label of a
  document is `DOCUMENT`, and the label of an anchor is `ANCHOR`.

The popup:

- reuses the `autocomplete-items` and `autocompletable-result-item` styles
- is a fixed popup in `<body>` (see the helpers) and stops the propagation
  of its clicks
- gets its position from the caret rectangle with `placeFixed()` and
  follows the caret line on scroll and on a window resize
- sends the request 150 ms after the last keystroke and aborts the
  previous request
- handles its keys in a capture listener on `document` and stops the key
  events. As a result, the field and the table view do not see Enter,
  Tab, Escape, and the arrow keys while the popup is visible.

`findTrigger()` reads the `[LINK:` syntax, and `linkTag()` writes the
`[LINK: <UID>]` syntax. Both functions relate to SDOC-SRS-149 (Inline
links). The grammar of `InlineLink` and `Anchor` in `grammar.py` relates
to SDOC-SRS-149 and SDOC-SRS-150, with a comment that points to
`link_widget.js` and `anchor_widget.js`. As a result, the traces of
SDOC-SRS-149 and SDOC-SRS-150 show every place that a syntax change
affects.

### Anchor widget implementation

`anchor_widget.js` with `anchor_widget.css` is the `anchor` widget. The
widget implements only `supports()` and `insert()`. `insert()` opens the
form at the rectangle of the field button.

The form:

- is a fixed popup in `<body>` (see the helpers). The form stops the
  propagation of its clicks and keys. The form keeps its offset from the
  field, so the form follows the field on scroll and on a window resize.
- checks the UID syntax with `UID_PATTERN`, the JavaScript form of
  `REGEX_UID` in `grammar.py`
- finds the anchors of the field text with a regular expression on the
  lines that start with `[ANCHOR: `
- asks `/autocomplete/link?q=<UID>` 150 ms after the last keystroke and
  aborts the previous request. The UID is taken if the first item has the
  same UID. Insert stays disabled until the response confirms that the
  UID is free.
- writes the tag with `insertBlock()`.

`UID_PATTERN`, `fieldAnchorUids()`, `titleSource()`, and `anchorTag()`
relate to SDOC-SRS-150 (Inline anchors).

### Text positions

The DOM-to-text mapping walks text nodes and `<br>` elements. If the
mapping does not match `innerText` (for example, when the field contains
other elements), the script cannot compute the caret line reliably. In
this case, the field has no button, and `lineRange()` returns null.

### Tests

The page objects in `tests/end2end/helpers/components/`:

- `field_widgets.py`: `FieldWidgets`, the caret, the field button, and the
  insert menu
- `table_editor.py`: `TableEditor(FieldWidgets)`, the table highlights
  and the editor modal
- `link_widget.py`: `LinkWidget(FieldWidgets)`, the popup of link targets
- `anchor_widget.py`: `AnchorWidget(FieldWidgets)`, the anchor form.

The page objects use the test IDs `field-widgets-button`,
`field-widgets-insert-menu`, `field-widgets-insert-<id>`,
`field-widgets-link-popup`, and `field-widgets-anchor-*`.

The table editor tests cover the button and the insert menu, see
[Table editor](../20261109_feat_table_editor/task.md).

`tests/end2end/screens/document/field_widgets/insert_links/` covers the
link widget:

- `@` with Enter, and `[LINK:` with a click
- Escape: the text stays, and the popup does not open again for the same
  trigger
- a query with a space that matches nothing closes the popup
- after the user deletes the closed trigger, a new `@` at the same place
  opens the popup
- the Link item of the insert menu with a query of two words.

`tests/end2end/screens/table/view_table_edit/edit_table_cell_statement_link_widget/`
covers the table view: the popup in a narrow cell, a click on a target
does not save the cell, and Escape does not cancel the cell.

`tests/end2end/screens/document/field_widgets/insert_anchors/` covers the
anchor widget: Escape, a UID with a wrong syntax, a UID of a node, a title
that the tag cannot hold, a title in double quotes, and a UID of an anchor
that is in the field text but not saved yet.

`tests/end2end/screens/table/view_table_edit/edit_table_cell_statement_anchor_widget/`
covers the anchor form in the table view: Escape and a click on Insert do
not cancel or save the cell.

`tests/unit_server/strictdoc/server/24_autocomplete_link/` covers the
endpoint: all kinds of targets, the match by UID and by title, the exact
UID first, the kind labels, the current document first, and a request
without `q`.
