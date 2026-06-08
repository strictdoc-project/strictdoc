# Inline Editing in Table View

## WHY

Table view presents a document as a flat, sortable overview of its nodes and
their fields. Until now, this view was read-only: any change — a TITLE, a
STATEMENT, a relation, a comment, document configuration, custom metadata —
required switching to Document view, locating the corresponding node, and
opening its edit form there.

This back-and-forth defeats the purpose of Table view as a working surface.
Table view is most useful exactly when a user reviews many nodes side by side
and wants to correct or fill in fields without losing that overview. The
feature must let users edit a document directly in Table view, cell by cell and
field by field, while keeping the table's compact, scannable layout intact in
both display and edit states.

Editing must respect the same rules as Document view: only fields declared in
the document grammar are editable, validation must match the SDOC grammar and
the existing backend transforms, and Markdown/RST markup handling must remain
consistent with the rest of the application. The feature must not change the
SDOC data model or introduce a parallel editing pipeline — it must reuse the
existing update transforms and validation through new table-specific endpoints
and forms.

## WHAT

Table view gains an explicit **edit mode**, toggled from the toolbar
(`[data-testid="table-toolbar-edit-btn"]`). Toggling it switches `.main` to
`[data-mode="edit"]`; CSS then reveals hover outlines and per-cell edit
indicators only in that mode. Display mode is unaffected and remains read-only.

In edit mode, the following become inline-editable:

- **Root document fields**, shown above the table in `<sdoc-meta>`:
  `TITLE`, `UID`, `VERSION`, `CLASSIFICATION`, `PREFIX`, and the custom
  metadata key-value list. `DATE` remains read-only.
- **Per-node table cells**, for every column produced by
  `enumerate_table_columns()`, when the node's grammar declares the field:
  - `TITLE`, `STATEMENT`, `RATIONALE` — single-line or multi-line
    contenteditable fields (the distinction is server-side; the DOM uses one
    unified `contenteditable` field type);
  - `COMMENT` — one or more comment fields edited together;
  - `RELATIONS` — relation rows with autocompletable UID and editable role,
    alongside read-only computed/derived relations;
  - `MultipleChoice` and other autocompletable fields — driven by a Stimulus
    autocomplete controller already present in the DOM;
  - any other grammar-defined dynamic field — a generic single-line
    contenteditable cell.
- A cell whose field is **not** declared in a node's grammar is rendered dimmed
  (`content-view-td--dimmed`) and stays read-only, even in edit mode.

Common behavior across all editable fields:

- clicking an editable display fetches and opens an inline editor in place,
  without navigating away or covering the table with a modal;
- only the targeted field is replaced; sibling cells, rows, and the rest of the
  document metadata remain untouched;
- saving happens on blur, on outside click, or on Ctrl/Cmd+Enter; Escape
  cancels and restores the previous display;
- a save is skipped when the submitted value is unchanged from the original;
- once a field reports a validation error, the UI blocks switching to another
  field until the error is resolved ("passive open"), so a user cannot lose
  in-progress corrections by clicking away;
- validation errors are rendered inline next to the offending field as
  `sdoc-form-error`, scoped to that field only — they never replace or
  reorder unrelated rows;
- unexpected `5xx` responses are never parsed as field errors; the UI shows one
  generic save-failure message and logs the full response to the console.

Custom metadata additionally supports renaming, adding, deleting, and
drag-and-drop reordering of entries — this is the subject of the dedicated
specification
[document_config_custom_meta.md](document_config_custom_meta.md), because
metadata is stored as an ordered list without persistent per-entry identifiers
and therefore cannot reuse the single-field save mechanism as-is.

Supporting table UX shipped alongside editing: column visibility driven by the
grammar union (with dimmed cells for fields absent from a node's own grammar),
sortable columns, sticky header, min/max column widths, and a TIPS modal
explaining the available interactions.

## HOW

### Editability and column layout

`view_object.is_table_cell_editable(node_type, field_name)` reports whether a
field is declared in the grammar for that node type;
`view_object.get_table_cell_edit_mode(node_type, field_name)` returns the
grammar-declared edit mode (`"autocomplete"`, `"singleline"`, `"multiline"`,
`"readonly"`). `td_by_edit_mode.jinja` maps these grammar values onto the DOM:
`"singleline"` and `"multiline"` both render as `data-field-type="contenteditable"`
— the same component and the same client-side handling, with the server
deciding the actual form shape (single line vs. multi line) when the inline
editor is requested.

Columns themselves come from `view_object.document.enumerate_table_columns()`,
which yields the union of fields declared across the document's grammar
elements. `TYPE` and `LEVEL` are always the two leading fixed columns.

### Shared JavaScript contract (`table_view_edit.js`)

All table inline editing is driven by one script attached to the container
marked `js-table_view_edit`. It depends on explicit attributes rather than CSS
classes or incidental structure:

- `js-table_view_edit-table` — the table element (for header/sort wiring);
- `js-table_view_edit-toggle` — the edit-mode toggle button;
- `js-table_view_edit-field="<type>"` — an editable field and its handling,
  where `<type>` is one of `contenteditable`, `comments`, `relations`,
  `autocomplete`;
- `js-table_view_edit-add-field` — links that add comment or relation rows
  into an already-open inline form;
- `js-table_view_edit-form` — the form that must be submitted for a field;
  fields look up their form with
  `field.querySelector('[js-table_view_edit-form]') || field.closest(...)`,
  which supports both layouts: a field that contains its own form (most table
  cells, root document config fields) and a field contained by one shared form
  (custom metadata rows);
- `js-table_view_edit-submit-unchanged` — marks creation fields whose empty
  initial state must still reach the backend, so the server can decide between
  silently skipping an empty row and returning a validation error.

`js-table_view_edit-custom_meta-row`, `-name`, `-value`, `-delete_action`, and
`-drag_handle` are additional table-specific hooks used only by custom
metadata rows (see the dedicated specification).

### Inline form lifecycle (GET → edit → POST → turbo-stream)

Every editable field follows the same request/response shape:

1. Clicking a display fetches an inline-edit partial from the URL in the
   field's `data-url` (e.g. `get_node_contenteditable_inline`,
   `get_node_comments_inline`, `get_node_relations_inline`,
   `get_document_config_field_inline`, `get_document_custom_meta_inline`).
   The request is accepted with `Accept: text/vnd.turbo-stream.html`
   (`TURBO_ACCEPT`).
2. The server returns a Turbo Stream that swaps the field's display content
   for an editable form (contenteditable `<div>`, comment fields, relation
   rows, or an autocomplete-backed control), scoped to that field's target
   `<div id="cell-{mid}-{FIELD}">` / `<div id="doc-field-{mid}-{FIELD}">`.
3. On blur, outside click, or Ctrl/Cmd+Enter, JS serializes and POSTs the
   field's form to the matching update endpoint
   (`update_node_field`, `update_node_field_multiline`, `update_node_comments`,
   `update_node_relations`, `update_document_config_field`,
   `update_document_custom_meta`).
4. The server validates through the existing transforms
   (e.g. `UpdateDocumentConfigTransform`, node field/relation/comment update
   commands) and returns either a success Turbo Stream that re-renders the
   field's display, or a validation Turbo Stream that re-renders only the
   active field together with its `sdoc-form-error` markers.

`"singleline"`, `"multiline"`, `"comments"`, and `"relations"` are handled
identically client-side via `openInlineCell` / `saveInlineCell`
(`INLINE_FIELD_TYPES`); the difference is entirely server-side — different GET
endpoints inject different form shapes, different POST endpoints process them.
`"autocomplete"` is the exception: its Stimulus controller is already present
in the DOM in display mode, edit-mode CSS toggles between `.cell-display` and
`.cell-edit-ac`, and saving POSTs straight to `update_node_field` via `fetch`.

### Root document fields vs. table cells

Root document fields (`UID`, `VERSION`, `CLASSIFICATION`, `PREFIX`, `TITLE`,
custom metadata) live in `<sdoc-meta>` above the table and use
`document_config_field.jinja` / `document_title.jinja`. They are editable
through `get_document_config_field_inline` /
`update_document_config_field`, keyed by `document_mid` and `field_name`,
and saved through `UpdateDocumentConfigTransform`. `DATE` uses
`document_meta_readonly_field.jinja` and exposes no editable affordance.

Table cells are keyed by `node_mid` and `field_name`/`field_type`, fetched and
saved through the corresponding `get_node_*_inline` / `update_node_*`
action pairs, and routed through the existing node update commands
(`CreateOrUpdateNodeCommand` and friends).

### Validation and error display

Validation errors arrive as `text/vnd.turbo-stream.html` responses scoped to
the active field (for relations and comments, keyed by field MID rather than
field name, so multiple comment fields don't collide). The active editor stays
open, the entered value is preserved, and `sdoc-form-error` elements are
inserted next to the offending control with `errors="true"` applied only to
that control. "Passive open" then prevents switching to another field until
the error is cleared, and a successful correction removes the
`data-validation-error` marker from the field. Plain `5xx` HTML error pages are
never treated as field-level errors — the UI shows one generic message and logs
the response.

### Saving discipline

`table_view_edit.js` keeps per-cell editing state in a `WeakMap` (rather than
custom DOM properties), deduplicates repeated triggers for one logical save
behind a per-cell in-flight promise (while still allowing parallel saves of
different cells), and skips the save entirely when the serialized form data is
unchanged from the original (`ATTR_SUBMIT_UNCHANGED` opts a field out of this
skip so empty creation rows still reach the backend). Autocomplete blur timers
are stored per cell and cancelled when an outside click triggers the save, to
avoid a delayed duplicate POST. Event handlers are extracted from `init()` into
named feature-local functions rather than nested closures.

### Custom metadata (separate detailed specification)

Custom metadata cannot reuse the single-field mechanism above because it has no
persistent per-entry identifier — it is stored as one ordered key-value list.
It is therefore wrapped in one persistent shared form
(`js-table_view_edit-form` with `display: contents`), addressed through
positional `form_key`s, and supports rename, add, delete, and drag-and-drop
reorder, all of which resubmit the complete ordered list. The full design —
shared form, local form keys, row structure, validation rules, and
ordering/deletion mechanics — is described in
[document_config_custom_meta.md](document_config_custom_meta.md).

### Supporting UI work

Alongside the editing mechanics, the branch also added: column sorting with
sort icons and a reset button; a sticky table header; min/max column width
constraints for meta and relation columns; an editable-cell hover indicator;
moving the Filter/Edit buttons into the page header; and a TIPS modal that
documents the available interactions to the user.

## Verification

The completed feature must be checked with:

- toggling edit mode on and off, and confirming display mode stays read-only;
- editing each root document field (`TITLE`, `UID`, `VERSION`,
  `CLASSIFICATION`, `PREFIX`) and confirming `DATE` has no editable affordance;
- editing each editable table cell type per node grammar
  (`TITLE`, `STATEMENT`, `RATIONALE`, `COMMENT`, `RELATIONS`,
  `MultipleChoice`/autocomplete, generic dynamic fields);
- confirming cells absent from a node's grammar render dimmed and read-only;
- save triggers: blur, outside click, Ctrl/Cmd+Enter, and Escape to cancel;
- skip-on-unchanged behavior, and that creation fields still submit when empty;
- validation error display, field-specific error scoping, passive-open
  blocking, and marker removal after a successful correction;
- generic handling of unexpected `5xx` responses;
- column visibility, sorting, sticky header, and column width constraints;
- the complete custom metadata lifecycle described in
  [document_config_custom_meta.md](document_config_custom_meta.md);
- regression tests for Document view's existing edit forms for the same
  fields.
