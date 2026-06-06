# Working context

## Current scope

- Task: inline editing of document custom metadata in Table view.
- Source of truth:
  `developer/tasks/20260606_table_view_edit_mode/document_config_custom_meta.md`.
- Current plan step: 6, prepare stable table-specific DOM hooks for delete
  and reorder without implementing either controller.

## State before step 6

- Steps 1-5 are implemented.
- Custom metadata rows share one persistent form.
- Existing values and new rows are edited inline.
- Saving serializes the complete metadata list in DOM order.
- Existing rows already have a wrapper and local `data-form-key`, but lack
  explicit hooks for the name, value, delete action, and drag handle.

## Step 6 decisions

- Use `js-table_view_edit-custom_meta-*` attributes as table-specific hooks.
- Keep the existing `data-form-key` as the row's local transport key.
- Add inert hidden `button type="button"` elements for delete and drag hooks.
- Do not add JavaScript behavior for delete or reorder in this step.
- Keep all new hooks in the table custom-metadata row template.

## Verification

- `git diff --check`: passed.
- Jinja template unit test:
  `pytest -q tests/unit/strictdoc/export/html/test_html_templates.py`:
  1 passed.
- Focused Table view end-to-end suite:
  `invoke test-end2end --focus edit_table`: 18 passed.
- Static search confirms all five new hooks exist only in
  `document_custom_meta_row.jinja`.
- The existing name/value hidden inputs remain descendants of each row
  wrapper, so moving complete wrappers changes their serialization order.
