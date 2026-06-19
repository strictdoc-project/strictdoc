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

### Existing name

- `[x]` Edit mode off does not open the name editor.
- `[x]` Escape restores the original name.
- `[x]` Empty name marks only the name control and preserves the row value.
- `[x]` Correcting an invalid name saves it without changing row order or
  value.

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
- `[x]` Key errors mark only the name control.
- `[x]` Value errors mark only the value control.
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

### TITLE → level and TOC coherence

A node's TITLE determines its participation in the document hierarchy:
nodes without TITLE have no level number and are absent from the TOC.
The `update_node_field` handler for TITLE detects the three change cases and
returns additional Turbo Streams beyond the TITLE cell itself.

- `[x]` Adding a TITLE (None → text): the LEVEL cell receives the node's new
  level number and the TOC gains the new entry — both in-place, without a
  reload. All sibling LEVEL cells that shifted are also updated.
- `[x]` Removing a TITLE (text → None): the LEVEL cell becomes empty/dimmed,
  sibling LEVEL cells shift, and the TOC entry disappears — in-place, without
  a reload.
- `[x]` Renaming a TITLE (text → other text): only the TOC entry updates to
  the new text; the LEVEL cell value is unchanged because the structural
  hierarchy was not affected.

### Other field types

- `[x]` Single-choice autocomplete save.
- `[x]` Multiple-choice autocomplete save.
- `[x]` Existing comment edit.
- `[x]` Comment add, empty add, and delete.
- `[x]` Relation add and delete.
- `[x]` Adding/removing two relations to two different nodes in one editing
  session and saving once refreshes the RELATIONS cells of the edited node
  and both linked nodes, without a reload. The cross-node refresh in
  `table__update_node_relations` walks `affected_related_nodes` with one
  loop regardless of relation count, so the 2-relation add/remove cases
  exercise the same code path as a 1-relation change would, plus they prove
  several extra turbo-stream blocks in one response are all applied -
  a single 2-relation test stands in for the 1-relation case on each side.

### Remaining gaps

- `[x]` Optional custom String field edit, proving the generic dynamic-field
  path rather than only reserved TITLE/STATEMENT/RATIONALE fields.

### TITLE coherence E2E files

- `[x]` `edit_table_cell_title_level_and_toc` — covers all three TITLE change
  cases in one fixture: None → text, text → other text, text → None.

## 4. Add Node

### Rendering and placement

- `[x]` Create a REQUIREMENT before the first existing node.
- `[x]` Create a REQUIREMENT as a child of an existing SECTION.
- `[x]` Create a REQUIREMENT from a separator in the middle of a long table.
- `[ ]` Create a node using the `after previous` placement.
- `[ ]` Assert the complete valid action set for the first, middle, and last
  separators.
- `[ ]` Assert that Add separators are hidden outside Table edit mode.
- `[ ]` Assert that an empty Table does not render Add separators.

### Grammar-aware defaults and restrictions

- `[x]` A node type with a required SingleChoice field can be created; the
  required field is prefilled with `TBD`.
- `[x]` A node type with a required String field can be created; the required
  field is prefilled with `TBD`.
- `[x]` A node type with all-optional fields and no auto-generated UID/MID
  receives `TBD` in the first available field by priority
  (`TITLE` → `STATEMENT` → `RATIONALE` → first String → first SingleChoice →
  first MultipleChoice), so the node is never saved completely empty.
- `[x]` Created REQUIREMENT nodes receive a generated UID.
- `[x]` The client receives the generated MID and locates the created row.
- `[ ]` Create more than one supported grammar element type.
- `[ ]` Autogenerated-content restrictions are enforced.

### Sorting and row filtering

- `[x]` A hidden node type blocks Add Node and shows the row-filter reason.
- `[x]` Active sorting blocks Add Node and shows the sorting reason.
- `[x]` Simultaneous sorting and row-filter blockers show both reasons and hide
  regular creation actions.
- `[x]` Each blocker exposes its matching inline reset action.
- `[x]` Clearing only one blocker leaves the other blocker active.
- `[x]` Clearing the final blocker restores actions in the same open menu.
- `[x]` Resetting sorting preserves the open menu's vertical viewport
  position.
- `[x]` Resetting the row filter preserves the open menu's vertical viewport
  position.
- `[x]` Sorting preserves the active edit cell's row position and edit state.
- `[x]` Row filtering completes the active cell's outside-click lifecycle and
  does not preserve its row position.

### Turbo refresh and viewport behavior

- `[x]` Successful creation replaces the Table body and increases the row
  count.
- `[ ]` Explicitly assert that edit mode remains active after creation.
- `[x]` Hidden columns remain hidden in the header and replacement body.
- `[x]` The new row preserves the initiating Add menu's top-left viewport
  position.
- `[x]` Creation does not automatically open an editable field.
- `[ ]` A generic network or HTTP 5xx failure shows an error without inserting
  response HTML into the Table body.
- `[ ]` A server-side placement or creatability rejection leaves the document
  unchanged and displays the returned error state.

### Current Add Node E2E files

- `[x]` `add_table_node_requirement_before_first`
- `[x]` `add_table_node_requirement_child_of_section`
- `[x]` `add_table_node_with_required_single_choice_field`
- `[x]` `add_table_node_with_required_string_field`
- `[x]` `add_table_node_tbd_fallback_all_optional`
- `[x]` `add_table_node_blocked_when_rows_hidden`
- `[x]` `add_table_node_blocked_when_sorted`

## 5. Delete Node

### Rendering and confirmation

- `[x]` Delete actions are hidden outside Table edit mode.
- `[x]` A deletable requirement exposes a delete action in its `TYPE` cell.
- `[x]` A deletable section exposes a delete action in its `TYPE` cell.
- `[x]` Clicking Delete opens the confirmation modal.
- `[x]` Cancelling confirmation keeps the node and table unchanged.

### Successful deletion

- `[x]` Confirming deletes a requirement row and persists the deletion.
- `[x]` Confirming deletes a section row and preserves valid document
  structure.
- `[x]` Successful deletion refreshes the Table body and TOC.
- `[x]` Table edit mode remains active after deletion.

### Restrictions and validation

- `[ ]` A node rejected by `can_delete_node()` has a visible disabled delete
  action.
- `[x]` A deletion validation error is shown in the confirmation modal.
- `[x]` A failed validation leaves the node and document unchanged.

### Delete Node E2E files

- `[x]` `delete_table_node_requirement`
- `[x]` `delete_table_node_section`
- `[x]` `delete_table_node_validation`

## Implementation order

### Custom metadata: completed

1. Existing name lifecycle, validation, and correction.
2. Existing value lifecycle and full-list/order preservation.
3. Existing value validation, correction, and Escape recovery.
4. Add success and empty cancellation.
5. Add validation matrix, field-specific markers, and correction.
6. Delete the only metadata row.
7. Delete/reorder rollback on forced HTTP failure.
8. No-metadata Add availability and rendered/raw value separation.

### Root node fields: completed

1. Document TITLE lifecycle and validation.
2. Config values: UID, VERSION, CLASSIFICATION, PREFIX.
3. Optional empty value and direct field switching.
4. DATE read-only behavior.

### Table cells: completed

1. Add one generic optional String-field test.
2. Keep the existing contenteditable, autocomplete, comments, relations, and
   validation suites unchanged unless the new tests expose a regression.

### Add Node: partially completed

1. Basic `before next` and `child of previous` creation.
2. Required Choice disabling.
3. Sorting and row-filter blockers with inline reset actions.
4. Viewport preservation for menus, active edit rows, and newly created rows.
5. Remaining placement, grammar-default, failure, and empty-state cases are
   listed above as required gaps.

### Delete Node: completed

1. Extract the `TYPE` cell partial and render the delete action in edit mode.
2. Add Table-local confirmation and confirmed deletion responses.
3. Cover requirement deletion, section deletion, cancellation, and validation.
4. Add dedicated coverage for the disabled permission state.
