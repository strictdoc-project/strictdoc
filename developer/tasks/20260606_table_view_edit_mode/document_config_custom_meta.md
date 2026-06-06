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
continuing to save custom metadata as one ordered list, without adding persistent
metadata identifiers or changing the SDOC data model.

## WHAT

The Table view shall present each custom metadata entry as a regular
document-level metadata row:

- the key is displayed in `sdoc-meta-label`;
- the value is displayed in `sdoc-meta-field`;
- existing entries expose the same editable-cell affordance as stable document
  configuration fields;
- clicking an existing entry edits only its value;
- adding metadata creates an inline row with editable key and value controls;
- saving an entry submits the complete custom metadata list in its current DOM
  order;
- validation errors remain attached to the active row without replacing the
  other metadata rows;
- the structure shall support later row deletion and drag-and-drop reordering
  without requiring persistent metadata IDs or backend model changes.

Existing metadata keys are immutable in this interaction. Renaming an existing
key is represented by deleting the entry and adding a new one.

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
`DocumentConfigFormObject`. Saving any custom metadata row serializes and submits
the complete form. The backend continues to use `UpdateDocumentConfigTransform`
to replace the complete ordered metadata list.

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
`display: contents`. The wrapper groups the label and value into one movable or
deletable unit without changing the grid layout.

The row contains:

- a hidden input with the raw metadata key;
- a value target with a hidden input containing the raw value;
- separately rendered display content produced by `render_metadata_value()`;
- an editable `sdoc-meta-field` connected to `table_view_edit.js`;
- table-specific DOM hooks for the row and its current `form_key`.

Raw values and rendered values must remain separate. Form submission uses the
raw hidden input, while display mode uses the rendered HTML.

### Editing an existing value

Clicking an existing metadata value requests an inline edit partial using
`document_mid` and `form_key`.

Turbo updates only the selected value target:

- the key label remains unchanged;
- other custom metadata rows remain unchanged;
- the value display is replaced by a single-line contenteditable control;
- blur or Ctrl/Cmd+Enter submits the shared form;
- a successful response replaces only the active value target with its display
  partial.

Although the UI edits one value, the POST always contains the complete metadata
list. This preserves the list-based backend contract and its current order.

### Adding metadata

The final metadata grid row contains the **Add new metadata** action. The Add
wrapper is one JS-managed inline field.

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
errors are rendered as `sdoc-form-error` elements.

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

If deletion fails, the UI must restore the removed row or re-render the metadata
block into a state consistent with the backend.

### Verification

The completed feature must be checked with:

- no custom metadata;
- one custom metadata entry;
- multiple entries;
- editing an existing value;
- adding a valid entry;
- all empty and partially empty Add cases;
- invalid key syntax;
- clearing an existing value;
- deleting an entry;
- preserving and changing metadata order;
- display and edit modes;
- blur and Ctrl/Cmd+Enter saves;
- regression tests for the existing Table view inline editors;
- regression tests for the existing Document view metadata form.
