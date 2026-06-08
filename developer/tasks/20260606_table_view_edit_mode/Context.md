# Working context

## Current scope

- Task: end-to-end coverage of all inline editing paths in Table view.
- Source of truth:
  `developer/tasks/20260606_table_view_edit_mode/document_config_custom_meta.md`.
- Test matrix:
  `developer/tasks/20260606_table_view_edit_mode/_test_cases.md`.

## Coverage decisions

- The matrix is grouped into custom metadata, root node fields, and table
  cells.
- Shared contenteditable behavior is tested once per distinct implementation
  path instead of repeating every save mechanism for every field.
- E2E selectors use `data-testid`; row-specific validation and document title
  test IDs were added where none existed.

## Added coverage

- Custom metadata:
  existing value lifecycle and validation; Add success, cancellation, and
  validation; deleting the only row; delete/reorder rollback; no-metadata Add;
  raw submitted value versus rendered display.
- Root node fields:
  document TITLE lifecycle and validation; UID, VERSION, CLASSIFICATION, and
  PREFIX values; direct field switching; optional empty value; read-only DATE.
- Table cells:
  generic optional custom String field through the dynamic-field path.
- The existing delete test now scopes rows and actions through `data-testid`
  instead of form keys or JavaScript hooks.

## Regression fixed

- Successful correction after inline validation did not remove
  `data-validation-error` from the field.
- `table_view_edit.js` now clears the marker after a successful save.

## Existing metadata name editing

- Existing custom metadata names are editable inline through a dedicated name
  target inside the existing label.
- Name and value editors submit the same complete ordered metadata form.
- `active_field_name` selects the name or value Turbo target for validation and
  successful updates.
- Renaming preserves the row value and position and does not introduce a
  persistent metadata identifier.
- Add-row validation now splits row errors between `name_errors` and
  `value_errors`, so `errors="true"` is set only on the affected control.
- The task specification and test matrix document the new name-editing and
  field-specific validation behavior.

## Custom metadata row layout follow-up

- Custom metadata display and Add UI now use persistent `sdoc-meta-row`
  wrappers with the shared CSS subgrid.
- Opening the Add editor no longer changes its wrapper from flex to
  `display: contents`, avoiding a full metadata-grid layout reconstruction.
- Dragging is armed from the move handle but uses the complete metadata row as
  the native drag source and drop geometry target.
- Drag/drop indicators are rendered on the row without changing its dimensions.

## Verification

- `git diff --check`: passed.
- Jinja template unit test:
  `pytest -q tests/unit/strictdoc/export/html/test_html_templates.py`:
  1 passed.
- Focused custom metadata end-to-end tests:
  `invoke test-end2end --focus edit_table_document_custom_meta --headless`:
  9 passed.
- Full focused Table view end-to-end suite:
  `invoke test-end2end --focus edit_table --headless`:
  30 passed, 314 deselected.
- `invoke lint-ruff-format`: passed.
- `invoke lint-ruff`: passed.
- `invoke lint-mypy`: passed, 268 source files checked.
- `invoke lint` could not start its code checks because the repository contains
  an existing non-conventional commit message: `DOCS: ASDFGHJK`.
