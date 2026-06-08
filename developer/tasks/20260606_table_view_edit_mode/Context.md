# Working context

## Current scope

- Task: inline editing of document custom metadata in Table view.
- Source of truth:
  `developer/tasks/20260606_table_view_edit_mode/document_config_custom_meta.md`.
- Current plan step: 7, delete custom metadata rows and save the remaining
  ordered list.

## State before step 7

- Steps 1-6 are implemented.
- Custom metadata rows share one persistent form.
- Each row has stable table-specific hooks for its wrapper, name, value,
  delete action, and future drag handle.
- Saving serializes the complete metadata list in DOM order.

## Step 7 decisions

- The delegated Table view click handler owns the delete interaction.
- Delete cancels any open inline editor, removes the complete row wrapper, and
  submits the remaining shared form with `action=delete`.
- The removed row and its next sibling are retained in memory until the
  request completes. Any HTTP or network error restores the row at its
  original position.
- The update endpoint accepts a delete action whose active form key is no
  longer present in the submitted metadata fields.
- A successful delete re-renders the complete shared metadata form. This
  normalizes positional form keys and prevents collisions with a later Add.
- No persistent metadata identifier or data-model change was introduced.

## Verification

- `git diff --check`: passed.
- Jinja template unit test:
  `pytest -q tests/unit/strictdoc/export/html/test_html_templates.py`:
  1 passed.
- New focused delete end-to-end test:
  `invoke test-end2end --focus edit_table_document_custom_meta_delete
  --headless`: 1 passed.
- Full focused Table view end-to-end suite:
  `invoke test-end2end --focus edit_table --headless`: 19 passed.
- `invoke lint-ruff-format`: passed after formatting the changed Python code.
- `invoke lint-ruff`: passed.
- `invoke lint-mypy`: passed, 268 source files checked.
- `invoke lint` could not start its code checks because the repository contains
  an existing non-conventional commit message: `DOCS: ASDFGHJK`.
