# Field widgets

## WHAT

Multiline fields have widgets that insert and edit markup elements. The
widgets work in server mode on two screens: the document screen (node
form) and the table view (inline cell form). The cells of the table editor
take the widgets that fit a table cell (see Widget contexts).

| Widget | Markup | Kind | Description |
|---|---|---|---|
| Table | RST, Markdown | Block | [Table editor](../20261109_feat_table_editor/task.md) |
| Link | RST, Markdown | Inline | [Link widget](#link-widget) |
| Anchor | RST, Markdown | Block | [Anchor widget](#anchor-widget) |

The widgets work only with RST and Markdown.

### Field button

While a form field has focus, one button shows in the left margin of the
field:

| Caret position | Button | Location | Click |
|---|---|---|---|
| In a block that a widget can edit | Edit (pencil icon) | Next to the first line of the block | Opens the widget editor for the block. |
| On a blank line outside such a block | Insert (`+`) | Next to the caret line | Opens the insert menu. |

The button hides on any other caret line, while the user types, and when
the field loses focus. The insert button shows only if a widget works in
the field.

A widget can add a second button under the edit button for its block. The
table widget adds the Format table button (wrench icon) for a misaligned
table.

### Insert menu

The insert menu has one item for each widget that works in the field. The
menu opens at the caret:

- when the user clicks the insert button
- when the user types `/` anywhere in the field, also inside a word.

While the menu is open, an `insert` placeholder marks the caret position.
The placeholder is not part of the field text and is never saved.

| Action | Result |
|---|---|
| Text typed after `/` | Filters the items by the start of a word of the label. If no item matches, the menu closes, and the text stays. |
| Arrow keys up and down | Move the active item. |
| Enter, Tab, or a click on an item | Removes `/` and the filter text, and inserts the element of the widget. |
| Escape, or the Close menu item | Closes the menu. The typed text stays, `/` included. |
| Arrow keys left and right, a click outside the menu, a caret move, a focus loss | Close the menu. |
| Typing after the insert button opened the menu | Closes the menu. |

Escape closes only the menu. In the table view, the cell stays in edit
mode.

Where the element goes:

- An inline widget (Link) writes its text at the caret, with a space
  before and after the text when the neighbor is not a space. On a blank
  line, the text forms its own paragraph, with blank lines around it.
- A block widget (Table, Anchor) writes its block as a new paragraph
  after the block of non-blank lines that holds the caret. The text at the
  caret stays as it is. On a blank line, the block takes the place of the
  line. Blank lines separate the block from its neighbors.

A widget can capture the input at the caret. Then `/` is plain text and
does not open the menu. The link widget does so after `[LINK:`, because a
UID can contain `/`.

### After a write

When a widget writes into the field:

- The page scrolls as little as needed to show the caret line. A caret
  below the visible area ends up at its bottom edge. A visible caret does
  not scroll the page.
- The written text has a highlight that fades out within a second. A
  widget highlights only its result, not a draft such as the `[LINK: `
  text before the user chooses a target.

### Link widget

The link widget writes a `[LINK: <UID>]` tag without a link title. A list
of link targets opens at the caret. The targets are the documents,
sections, nodes, and anchors with a UID. The targets of the current
document come first.

The list opens on these triggers:

| Trigger | Query | The tag replaces |
|---|---|---|
| `[LINK:` | The text after `[LINK:`, up to the caret | `[LINK:` and the query |
| Link item of the insert menu | The item writes `[LINK: ` at the caret, then the user types the query | `[LINK:` and the query |

The list behavior:

- A query can have several words. A target matches if its UID and title
  together contain every word. A query that matches no target shows "No
  matches found".
- Only typing opens the list. A caret move only closes the list, when the
  caret leaves the trigger. As a result, a click into an old trigger does
  not open the list.
- The list stays hidden until the first response arrives. While the list
  is hidden, the keys work as usual.
- The arrow keys move the selection. Enter or Tab writes the selected
  target. A click on a target writes the target.
- Escape closes only the list and keeps the typed text. In the table view,
  the cell stays in edit mode.
- After Escape, the list stays closed until the user starts another
  trigger.
- While the caret is after `[LINK:`, a typed `/` is part of the query.

### Anchor widget

The anchor widget writes an `[ANCHOR: <UID>]` or `[ANCHOR: <UID>, <title>]`
tag. An anchor tag is block-level: it is a block widget. The widget does
not edit existing anchors.

The Anchor item of the insert menu opens a form under the caret position:

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
| `supports(markup, context)` | yes | True if the widget works in a field with this markup and in this context (see Widget contexts). |
| `insert(field, at, rect)` | yes | Inserts a new element. For an inline widget, `at` is the text offset of the caret. For a block widget, `at` is the caret line. `rect` is the viewport rectangle of the caret position, for a widget that shows its own popup there. |
| `inline` | no | True for an inline widget. A block widget leaves it out. |
| `scan(field, lines, markup)` | no | Called after every change of the text of a field where the widget works. |
| `forget(field)` | no | Called when the field is no longer in the DOM. The widget drops its data about the field. |
| `capturesInput(field)` | no | True if the text at the caret belongs to the widget, for example the query of an unfinished tag. Then a typed `/` does not open the insert menu. |
| `blockAt(field, line)` | no | Returns the block `{start, end, ...}` that holds the line, or null. |
| `editTitle` | no | Title of the edit button. |
| `edit(field, block)` | no | Edits a block from `blockAt()`. |
| `activate(field, block)` | no | Called on every caret move with the block that holds the caret, or null. Also called with null when the field loses focus. |
| `extraAction(field, block)` | no | Returns `{icon, title, run}` for a second button under the edit button, or null. `icon` names an icon in `components/field_widgets/icons.jinja`. The button calls `run()`. The table widget uses it for the Format table button (icon `format`, a wrench). |

Any widget can have `scan()`, `forget()`, and `capturesInput()`. The
members from `blockAt()` to `extraAction()` are for widgets that recognize
their own blocks in the field text, such as tables.

`StrictDoc.fieldWidgets` also gives the widgets eight helpers:

- `hasWidget(field, id)`: true if the widget works in the field.
- `lineRange(field, start, end, startColumn = 0)`: a DOM range for the
  lines, from the column `startColumn` of the first line, or null if the
  script cannot map the field DOM to its text.
- `textBeforeCaret(field)`: the field text before the caret, or null if
  the caret is not in the field or the script cannot map the field DOM to
  its text.
- `insertInline(field, offset, text, options)`: writes the text at the
  offset, with spaces around it, or as a new paragraph on a blank line
  (`inlineFormsParagraph()`). The caret goes after the text.
- `insertBlock(field, line, blockLines, options)`: writes the lines as a
  new paragraph after the block that holds the line, or in place of the
  line if it is blank. Blank lines separate the block from the text
  around it.
- `replaceLines(field, start, end, newLines, options)`: writes the lines in
  place of the lines from `start` to `end`. With `{keepCaret: true}`, the
  caret stays where the user put it, and a field without focus does not
  get the focus. The table widget uses this option to align a table after
  the caret has left it.
- `replaceText(field, from, to, text)`: writes the text in place of the
  characters from `from` to `to` and puts the caret after the text.
- `placeFixed(element, rect)`: puts a fixed element under the rectangle,
  or above it if there is no room below, inside the viewport.

The helpers that write text highlight the written text, because a widget
writes its result. A widget that writes a draft passes
`{highlight: false}` to `insertInline()` or `insertBlock()`. The link
widget does so for `[LINK: `.

A widget popup that the form must not cut goes into `<body>` with a fixed
position. Inside the form, the overflow of `sdoc-form-grid` would cut the
popup: `sdoc-node` is a CSS container, and a container is the containing
block of its fixed descendants. In the table view, a click or a key
outside the edited cell saves or cancels the cell. As a result, such a
popup stops the propagation of its clicks and keys.

A widget script can load after `field_widgets.js` initializes the fields.
As a result, `register()` scans the fields that already exist.

### Widget contexts

The context says where the field is. Each widget decides in `supports()`
in which contexts it works, because what fits depends on the place and on
the format.

| Context | Field | Field button |
|---|---|---|
| `field` | A multiline field of a form: the node form or the table view cell form. | Yes |
| `table-cell` | A cell of the table editor. The cell text goes into one table cell of the field. | No, `/` opens the menu |

Where the widgets work:

| Widget | `field` | `table-cell` | Why |
|---|---|---|---|
| Link | Yes | Yes | A LINK tag is inline text. |
| Anchor | Yes | No | An ANCHOR tag must start a line of the field text. In the field, a line of an RST cell starts with `\|`, and a Markdown table row is one line. |
| Table | Yes | No | The editor does not support nested tables. |

A new widget can work in a cell of one format only. For example, in
Markdown a table cell holds only inline text, but in RST a cell can also
hold blocks such as lists or code. Such a widget checks both arguments:
`(markup, context) => context === 'field' || markup === 'RST'`.

### Field integration

- `StrictDoc.onInsert()` initializes every multiline contenteditable,
  including the fields that Turbo inserts later. The script has no
  `MutationObserver` of its own.
- The field markup comes from the `document_markup` input of the form.
  The table view cell form gets this input from the
  `table__get_node_contenteditable_inline` route.
- A field outside a form, such as a cell of the table editor, gets the
  widgets through attributes: `data-field-widgets-markup` (the markup
  that a form field takes from `document_markup`),
  `data-field-widgets-document-mid` (the document for the order of link
  targets), and `data-field-widgets-context` (the context for
  `supports()`; without it, the context is `field`).
- The button goes after the hidden textarea of the field, because
  `editable_field.js` finds the textarea through
  `editable.nextElementSibling`. The button is absolutely positioned in
  `sdoc-form-field`, so the button scrolls with the field. The edit
  button and the extra button take their SVG icons from
  `components/field_widgets/icons.jinja`.
- The source text is the `innerText` of the field, the same value that
  `editable_field.js` saves.
- Delegated `input`, `selectionchange`, `pointerup`, and `focusout`
  listeners on `document` rescan the field and update the button. On
  `focusout`, the widgets get `activate()` with null, so a widget can act
  when the user leaves the field, for example, before the form is sent.
  After `input`, the script records the caret position. The button stays
  hidden until the caret moves elsewhere.
- A `Map` holds the state of each field. A rescan removes the entries of
  the fields that are no longer in the DOM and calls `forget()` of every
  widget for each removed field.

Insert menu:

- The `input` listener opens the menu when the user types `/`
  (`inputType` `insertText`), unless a widget captures the input. The
  menu remembers the offset of `/`, and the text between `/` and the caret
  is the query.
- The placeholder is an empty `contenteditable="false"` element at the
  caret. Its `insert` text comes from CSS `::before`, so `innerText` does
  not include it. The placeholder splits a text node of the field, so
  the field is scanned again after the placeholder is inserted and
  removed. Otherwise `lineRange()` would use the old text nodes.
- The menu is a fixed popup in `<body>` (see the helpers), placed with
  `placeFixed()` at the placeholder. The menu stops the propagation of
  its clicks and follows the placeholder on scroll and on a window resize.
- A capture listener on `document` handles the menu keys and stops them,
  so the field and the table view do not see them. In the table view,
  Escape in a field would cancel the cell edit.
- The insert menu and the widget popups have `z-index: 100000`, above the
  modals (`sdoc-backdrop`, 99999), so they work in the table editor. The
  insert menu rule includes `.dropdown_menu` to be stronger than its
  `z-index`.

Writes:

- A write replaces the field content with one text node and dispatches a
  bubbling `input` event. `editable_field.js` handles the event and
  updates the hidden textarea.
- Scrolling to the caret: the browser does not scroll to a caret that a
  script sets. The script first writes the text with a marker element at
  the caret and calls `scrollIntoView({block: 'nearest'})` on it. The
  marker is an inline block with a zero-width space, so it has the height
  of the line: Chrome scrolls an empty or inline marker only to the top of
  the line. The field gets the focus with `preventScroll`, because a
  focus scroll stops the smooth scroll of `.main`.
- The highlight of the written text uses the CSS Custom Highlight API
  (`::highlight(field-widgets-written)`). `::highlight()` cannot be
  animated, so a class on the field animates the custom property
  `--field-widgets-written-alpha` (`@property`), and the highlight takes
  its color from the property. When the animation ends, the highlight is
  removed.

### Link widget implementation

`link_widget.js` with `link_widget.css` is the `link` widget, an inline
widget. The widget has no blocks of its own. As a result, the widget
implements only `supports()`, `insert()`, and `capturesInput()`. The
widget listens to `input` itself and checks the field with `hasWidget()`.
`insert()` writes `[LINK: ` with `insertInline()` and
`{highlight: false}`, and the `input` event of this write opens the popup.

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
  the document on the screen, or the `data-field-widgets-document-mid`
  attribute of a field outside a form. The table view cell form gets the
  input from the `table__get_node_contenteditable_inline` route.
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

`anchor_widget.js` with `anchor_widget.css` is the `anchor` widget, a
block widget. The widget implements only `supports()` and `insert()`.
`insert()` opens the form at the rectangle of the caret position.

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

- `field_widgets.py`: `FieldWidgets`, the caret, the field text, the field
  button and the extra button, and the insert menu with its placeholder
- `table_editor.py`: `TableEditor(FieldWidgets)`, the table highlights
  and the editor modal
- `link_widget.py`: `LinkWidget(FieldWidgets)`, the popup of link targets
- `anchor_widget.py`: `AnchorWidget(FieldWidgets)`, the anchor form.

The page objects use the test IDs `field-widgets-button`,
`field-widgets-extra-button`, `field-widgets-insert-menu`,
`field-widgets-insert-<id>`, `field-widgets-menu-close`,
`field-widgets-placeholder`, `field-widgets-link-popup`, and
`field-widgets-anchor-*`.

The table editor tests cover the button and the insert menu of the
`+` button, see [Table editor](../20261109_feat_table_editor/task.md).

`tests/end2end/screens/document/field_widgets/insert_menu/` covers the
insert menu of `/`:

- `/` inside a word opens the menu with the placeholder, and the
  placeholder is not in the field text
- Escape and the Close menu item keep `/`
- a query that matches no item closes the menu and keeps the text
- a block widget goes after the paragraph of two lines, and at the end of
  the field it gets a blank line before it only
- after the write, the page scrolls to the caret: the test adds space
  above the field, so the page can scroll, and puts the caret line at the
  bottom of the viewport. The check waits for the smooth scroll and
  compares the caret with the scroll container, which ends above the page
  footer.

`tests/end2end/screens/document/field_widgets/insert_links/` covers the
link widget:

- `[LINK:` with Enter and with a click
- Escape: the text stays, and the popup does not open again for the same
  trigger; `/` after `[LINK:` does not open the insert menu
- after the user deletes the closed trigger, a new trigger at the same
  place opens the popup
- `/` inside a word with the query `li`: the link goes to the caret with
  spaces around it
- the Link item of the insert button on a blank line: the link forms its
  own paragraph, and a query of two words finds the target
- before a space, the link gets no space after it.

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

The highlight of the written text has no automatic test: the highlight
fades out within a second, so a check would depend on the test timing.
