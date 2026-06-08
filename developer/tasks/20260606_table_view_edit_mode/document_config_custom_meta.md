# Inline Editing of Document Custom Metadata in Table View

## WHY

Document custom metadata must be editable directly in Table view, consistently
with the other document-level fields displayed above the table.

Unlike stable document configuration fields such as `UID`, `VERSION`,
`CLASSIFICATION`, and `PREFIX`, custom metadata entries have no persistent
identifier in the StrictDoc data model. They are stored as an ordered list of
key-value pairs. Consequently, an individual custom metadata entry cannot be
updated through the same single-field mechanism used for stable document
configuration fields.

The feature must therefore provide field-like inline editing in the UI while
continuing to save custom metadata as one ordered list, without adding
persistent metadata identifiers or changing the SDOC data model.

## WHAT

The Table view shall present each custom metadata entry as a regular
document-level metadata row:

- the key is displayed in `sdoc-meta-label`;
- the value is displayed in `sdoc-meta-field`;
- existing entries expose the same editable-cell affordance as stable document
  configuration fields;
- clicking an existing key or value edits only that field;
- adding metadata creates an inline row with editable key and value controls;
- saving an entry submits the complete custom metadata list in its current DOM
  order;
- validation errors remain attached to the active row without replacing the
  other metadata rows;
- deleting an entry immediately saves the remaining metadata list;
- drag-and-drop reordering immediately saves the new metadata order;
- failed deletion or reordering restores the previous UI state;
- deletion and reordering do not require persistent metadata IDs or backend
  model changes.

Existing metadata keys can be renamed inline. Renaming keeps the row in its
current position and submits the complete ordered metadata list.

## HOW

### Shared form

All custom metadata rows are permanently enclosed by one form:

```html
<form js-table_view_edit-form style="display: contents">
  <!-- custom metadata rows -->
</form>
```

`display: contents` keeps the form transparent to the `sdoc-meta` grid.
`sdoc-meta-label` and `sdoc-meta-field` remain the visual grid items, so display
mode retains the established document metadata layout.

The form also contains the document configuration values required by
`DocumentConfigFormObject`. Saving any custom metadata row serializes and
submits the complete form. The backend continues to use
`UpdateDocumentConfigTransform` to replace the complete ordered metadata list.

### Local form keys

Each row receives a local `form_key`, for example `custom_meta_0`. This key is:

- used in input names, DOM targets, and validation keys;
- valid only for the current form render;
- derived from the row position;
- not a StrictDoc MID;
- not stored in the SDOC document;
- not a persistent identity for the metadata entry.

The form fields use the following names:

```text
metadata[form_key][name]
metadata[form_key][value]
```

Validation errors use:

```text
METADATA[form_key]
```

Nested form keys must contain only letters, digits, and underscores because the
shared form-data parser supports only those characters in bracketed key
segments. Unsaved rows use a distinct prefix such as `new_custom_meta_0`, which
allows the endpoint to distinguish a new entry from an existing positional row.

### Row structure

Each existing metadata entry has one table-specific row wrapper with
the custom element `sdoc-meta-row`. The row is a grid using
`grid-template-columns: subgrid`, so it shares the four column tracks defined
by the parent `sdoc-meta`:

```text
[move action] [key] [value] [delete action]
```

The wrapper gives the complete row its own visual box and groups its controls,
label, and value into one movable or deletable unit.

The row contains:

- a hidden input with the raw metadata key;
- a value target with a hidden input containing the raw value;
- separately rendered display content produced by `render_metadata_value()`;
- editable key and value targets connected to `table_view_edit.js`;
- table-specific DOM hooks for the row, name, value, delete action, drag
  handle, and current `form_key`.

Raw values and rendered values must remain separate. Form submission uses the
raw hidden input, while display mode uses the rendered HTML.

### Editing an existing key or value

Clicking an existing metadata key or value requests an inline edit partial
using `document_mid`, `form_key`, and `field_name`.

Turbo updates only the selected target:

- the other field remains unchanged;
- other custom metadata rows remain unchanged;
- the selected display is replaced by a single-line contenteditable control;
- blur or Ctrl/Cmd+Enter submits the shared form;
- a successful response replaces only the active key or value target with its
  display partial.

Although the UI edits one field, the POST always contains the complete metadata
list. This preserves the list-based backend contract and its current order.
`active_field_name` identifies whether the response must update the `name` or
`value` target.

### Adding metadata

The final metadata grid row is also an `sdoc-meta-row` and contains the
**Add metadata** action. The Add wrapper is one JS-managed inline field and
remains the same grid row in both display and editing states.

When opened, Turbo replaces its content with:

- an editable key control in the label area;
- an editable value control in the field area;
- an `active_form_key` identifying the new row.

Both controls belong to the persistent shared form. On successful save, Turbo
replaces the editing Add wrapper with:

1. a normal display row for the newly saved metadata;
2. a fresh Add wrapper below it.

A completely empty new row represents a cancelled Add operation and is skipped
without writing the document. A partially completed row must be validated and
must remain open when invalid.

### Validation

Backend validation must prevent writing metadata that cannot be parsed back from
the SDOC file.

Metadata keys must match the SDOC grammar:

```text
[a-zA-Z_][a-zA-Z0-9_-]*
```

Metadata values must not be empty because the SDOC grammar requires a
`SingleLineString`.

The required behavior is:

- empty new key and empty new value: skip the row;
- empty key with a non-empty value: validation error;
- valid key with an empty value: validation error;
- syntactically invalid key: validation error;
- clearing the value of an existing entry: validation error.

On validation failure, the server returns a Turbo Stream for the active row
only. The inline editor remains open, entered values are preserved, and the
errors are rendered as `sdoc-form-error` elements. `errors="true"` is applied
only to the control described by the error: key errors mark the name control,
and value errors mark the value control.

### Turbo and error responses

Successful and validation responses use `text/vnd.turbo-stream.html`.
Unexpected `5xx` HTML error pages must never be inserted line by line as field
validation errors. The UI shows one generic save error, while the complete
server response is written to the developer console.

### JavaScript DOM contract

Table inline editing must depend on explicit table-specific attributes rather
than CSS classes or incidental HTML structure:

- `js-table_view_edit` identifies the feature container;
- `js-table_view_edit-field` identifies an editable field and its behavior;
- `js-table_view_edit-form` identifies the form submitted for the field;
- `js-table_view_edit-submit-unchanged` identifies creation fields whose empty
  initial state must reach the backend for skip or validation handling.

Custom metadata rows additionally use:

- `js-table_view_edit-custom_meta-row` for the complete movable row;
- `js-table_view_edit-custom_meta-name` for the editable label;
- `js-table_view_edit-custom_meta-value` for the editable value;
- `js-table_view_edit-custom_meta-delete_action` for deletion;
- `js-table_view_edit-custom_meta-drag_handle` for drag initiation.

The form lookup supports both established layouts:

```javascript
field.querySelector(`[${ATTR_FORM}]`) ||
field.closest(`[${ATTR_FORM}]`)
```

Most table fields contain their own form. Custom metadata fields are contained
by one shared form. Both layouts therefore use the same save, blur,
Ctrl/Cmd+Enter, Escape, validation, and passive-open mechanisms.

### Ordering and deletion

The order of custom metadata row wrappers in the shared form defines the order
of serialized inputs and therefore the order written to the SDOC document.

Reordering shall operate by moving complete row wrappers within the shared form.
Deletion shall remove one row wrapper and then submit the remaining list. These
interactions must use table-specific hooks and must not introduce persistent
metadata identifiers.

Drag-and-drop reordering is available only in Table edit mode. A drag starts
only from the row's drag handle. The Add row is not draggable and cannot be a
drop target.

The complete `sdoc-meta-row` is the native draggable element, so the browser
renders the drag preview from that row rather than from only the move-action
container. Pointer interaction on the drag handle arms the row for dragging;
drag attempts from the editable key or value are rejected.

The row has a reliable visual bounding box. Drop position is calculated from
the target `sdoc-meta-row`: dropping in its upper or lower half inserts the
dragged row before or after it.

Deletion and reordering immediately submit the complete shared form:

```text
action=delete
action=reorder
```

`active_form_key` identifies the affected row for the request, but block
actions do not require that key to remain among the submitted metadata fields.
This is required when a row has already been removed from the DOM.

After a successful deletion or reorder, Turbo replaces the complete shared
custom metadata form. The server-rendered form normalizes positional
`form_key` values so later edit, Add, delete, and reorder operations cannot
collide with stale keys.

Before mutating the DOM, the client retains enough information to restore the
affected row at its original position. On an HTTP or network error, deletion
and reordering must restore the previous UI state.

The Table implementation remains local to `table_view_edit.js`. The existing
`draggable_list_controller.js` is not reused because it is designed for `li`
document-tree nodes, hierarchical drop positions, and a dedicated node-move
endpoint.

### Verification

The completed feature must be checked with:

- no custom metadata;
- one custom metadata entry;
- multiple entries;
- editing an existing value;
- renaming an existing key;
- adding a valid entry;
- all empty and partially empty Add cases;
- invalid key syntax;
- field-specific error markers for key and value validation;
- clearing an existing value;
- deleting an entry;
- preserving and changing metadata order;
- immediate persistence after deletion and drag-and-drop reordering;
- normalized positional form keys after deletion and reordering;
- restoration of the previous UI state after failed block actions;
- display and edit modes;
- blur and Ctrl/Cmd+Enter saves;
- regression tests for the existing Table view inline editors;
- regression tests for the existing Document view metadata form.
