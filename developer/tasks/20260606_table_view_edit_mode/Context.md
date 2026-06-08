# Working context

## Current scope

- Task: inline editing of document custom metadata in Table view.
- Source of truth:
  `developer/tasks/20260606_table_view_edit_mode/document_config_custom_meta.md`.
- Current work: drag-and-drop reordering of existing custom metadata rows.

## State before reorder

- Add, edit, validation, and delete are implemented.
- Custom metadata rows share one persistent form.
- Each row has stable table-specific hooks for its wrapper, name, value,
  delete action, and drag handle.
- Saving serializes the complete metadata list in DOM order.

## Reorder decisions

- Reorder remains scoped to Table custom metadata in `table_view_edit.js`; the
  tree-specific `draggable_list_controller.js` is not reused.
- Drag starts only from
  `js-table_view_edit-custom_meta-drag_handle` in edit mode.
- The row wrapper uses `display: contents`, so drop geometry comes from its
  visual metadata label rather than the wrapper bounding box.
- Dropping moves the complete row wrapper in the shared form and immediately
  submits the full form with `action=reorder`.
- The endpoint treats delete and reorder as block actions that do not require
  an active field to remain in the submitted metadata list.
- A successful reorder re-renders the complete shared form, normalizing
  positional form keys for later edit, Add, delete, or reorder operations.
- Any HTTP or network failure restores the moved row at its original sibling.
- No persistent metadata identifier or data-model change was introduced.
- E2E drag selectors use the move button test ID
  `form-move-field-action-form-field-metadata` and row-specific test IDs.

## Verification

- `git diff --check`: passed.
- Jinja template unit test:
  `pytest -q tests/unit/strictdoc/export/html/test_html_templates.py`:
  1 passed.
- Focused custom metadata delete and reorder end-to-end tests:
  `invoke test-end2end --focus edit_table_document_custom_meta --headless`:
  2 passed.
- Full focused Table view end-to-end suite:
  `invoke test-end2end --focus edit_table --headless`: 20 passed.
- `invoke lint-ruff-format`: passed.
- `invoke lint-ruff`: passed.
- `invoke lint-mypy`: passed, 268 source files checked.
- `invoke lint` could not start its code checks because the repository contains
  an existing non-conventional commit message: `DOCS: ASDFGHJK`.
