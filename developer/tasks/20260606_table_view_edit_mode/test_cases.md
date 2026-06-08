# Table View Inline Editing Test Matrix

The matrix is organized by behavior contracts. Shared behavior such as Escape,
blur saving, Cmd/Ctrl+Enter, and passive-open does not need to be repeated for
every field when one representative from each distinct implementation path is
covered.

Status:

- `[x]` covered by an existing end-to-end test;
- `[ ]` missing and required;
- `[-]` intentionally covered by another representative contract.

## 1. Custom metadata

### Existing value

- `[x]` Edit mode off does not open the value editor.
- `[x]` Escape restores the original value.
- `[x]` Blur saves one value without changing other rows or their order.
- `[x]` Cmd/Ctrl+Enter saves an existing value.
- `[x]` Empty value returns validation, preserves the editor, and marks the
  control with `errors="true"`.
- `[x]` Exactly one row-scoped error is rendered in the expected location.
- `[x]` Correcting an invalid value saves it and removes the error.
- `[x]` Escape after validation restores the original value and removes the
  error.

### Add

- `[x]` Add opens editable name and value controls.
- `[x]` Valid name/value saves a row at the end and restores a fresh Add action.
- `[x]` A completely empty Add is cancelled without writing the document.
- `[x]` Empty name with a value returns a row-scoped validation error.
- `[x]` Valid name with an empty value returns a validation error.
- `[x]` Invalid name syntax returns a validation error.
- `[x]` Entered name/value survive validation.
- `[x]` Correcting an invalid Add saves the row.
- `[-]` Cmd/Ctrl+Enter uses the same contenteditable save path as an existing
  value and is covered there.

### Delete and reorder

- `[x]` Delete removes one selected middle row and preserves the others.
- `[x]` Delete of the only row removes the complete `METADATA` block.
- `[x]` Drag-and-drop persists the new DOM order.
- `[x]` Successful block actions normalize positional form keys.
- `[x]` Failed delete restores the removed row.
- `[x]` Failed reorder restores the previous order.

### Rendering and regression

- `[x]` No metadata still exposes the Add action in edit mode.
- `[x]` Raw submitted value and rendered display value remain separate.
- `[-]` One and several rows are covered by add/edit/delete/reorder fixtures.
- `[x]` Full `edit_table` regression suite covers existing Table editors.

## 2. Root node fields

Representative fields: document `TITLE`, `UID`, `VERSION`,
`CLASSIFICATION`, and `PREFIX`.

- `[x]` Edit and blur-save document TITLE.
- `[x]` Escape restores document TITLE.
- `[x]` Empty document TITLE returns validation and can be corrected.
- `[x]` Edit and save each config value field.
- `[x]` Empty optional config field is saved as absent.
- `[x]` Switching directly between root fields saves the first and opens the
  second.
- `[-]` Cmd/Ctrl+Enter uses the shared contenteditable path covered by custom
  metadata and table cells.
- `[-]` Unchanged-form skip and passive-open are shared paths covered by table
  cell tests.
- `[x]` Read-only DATE does not become editable.

## 3. Table cells

### Contenteditable fields

- `[x]` Edit mode off prevents opening an inline editor.
- `[x]` TITLE Escape and blur save.
- `[x]` STATEMENT Escape and blur save.
- `[x]` RATIONALE blur save.
- `[x]` Cmd/Ctrl+Enter save.
- `[x]` Unchanged multiline value does not rewrite line endings.
- `[x]` Single-line Enter and paste strip newlines.
- `[x]` Required TITLE and STATEMENT validation.
- `[x]` Validation recovery with Escape.
- `[x]` Passive-open and field switching behavior.

### Other field types

- `[x]` Single-choice autocomplete save.
- `[x]` Multiple-choice autocomplete save.
- `[x]` Existing comment edit.
- `[x]` Comment add, empty add, and delete.
- `[x]` Relation add and delete.

### Remaining gaps

- `[x]` Optional custom String field edit, proving the generic dynamic-field
  path rather than only reserved TITLE/STATEMENT/RATIONALE fields.

## Implementation order

### Custom metadata: completed

1. Existing value lifecycle and full-list/order preservation.
2. Existing value validation, correction, and Escape recovery.
3. Add success and empty cancellation.
4. Add validation matrix and correction.
5. Delete the only metadata row.
6. Delete/reorder rollback on forced HTTP failure.
7. No-metadata Add availability and rendered/raw value separation.

### Root node fields: completed

1. Document TITLE lifecycle and validation.
2. Config values: UID, VERSION, CLASSIFICATION, PREFIX.
3. Optional empty value and direct field switching.
4. DATE read-only behavior.

### Table cells: completed

1. Add one generic optional String-field test.
2. Keep the existing contenteditable, autocomplete, comments, relations, and
   validation suites unchanged unless the new tests expose a regression.
