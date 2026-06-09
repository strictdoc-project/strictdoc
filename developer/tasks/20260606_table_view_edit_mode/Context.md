# Working context

## Current scope

- Task: implement Add Node in Table edit mode.
- Source of truth:
  `docs/strictdoc_11_developer_guide.sdoc`,
  `developer/tasks/20260606_table_view_edit_mode/task.md`,
  `developer/tasks/20260606_table_view_edit_mode/task__document_config_custom_meta.md`,
  `developer/tasks/20260606_table_view_edit_mode/task__add_node.md`.

## Agreed product decisions

- Creation is immediate: selecting a menu action creates and persists the node
  at once.
- Add separators exist before, between, and after visible table rows.
- Separator menus may offer `before next`, `after previous`, and
  `child of previous` where structurally valid.
- All grammar elements are listed.
- Required String fields may be auto-filled with `TBD`.
- Required Choice fields are never auto-selected; such node types are disabled
  in the Table Add menu.
- Add actions are blocked while table sorting is active or any node types are
  hidden through the rows filter.
- Empty Table view creation is out of scope.
- Shared router changes are allowed only as minimal Table-specific endpoints.

## Implementation notes

- Reuse `RequirementFormObject.create_new()`, `CreateOrUpdateNodeCommand`,
  document write/export flow, and Turbo refresh of the document content.
- Keep most behavior feature-local to the Table templates, CSS, JS, and tests.
- The existing worktree already contains draft Table add-row template changes;
  these are treated as in-progress local work, not reverted.

## Progress

- Recreated task `Context.md`.
- Implemented Table Add separators, feature-local add menu UI, and
  server-side `/actions/table/add_node`.
- Added grammar-aware blocking for required choice types and for types that
  would remain completely empty.
- Added runtime blocking when sorting is active or row types are hidden.
- A blocked Add menu hides node-creation actions and lists every active
  blocker. Each blocker has an inline reset action; the current menu remains
  open and returns to normal only after all blockers are cleared.
- Implemented viewport-anchor behavior:
  - creation does not open or focus a field;
  - the new row preserves the initiating Add menu area's top-left viewport
    coordinates;
  - resetting sorting or the rows filter preserves the open menu's vertical
    viewport position;
  - sorting preserves the row position and edit state of an active edit cell
    when no Add menu is open;
  - row filtering intentionally does not preserve an active edit cell.
- `table_view.js` emits before/after DOM events for sorting and row-visibility
  changes. `table_view_edit.js` consumes this event contract and compensates
  the `.main` scroll container without importing toolbar internals.
- Browser-native scroll anchoring is disabled only for the Table edit `.main`
  container. CSS also disables smooth scrolling while edit mode is active, so
  the viewport-anchor JavaScript does not need to mutate scrolling styles.
- Hidden columns do not block node creation. After Turbo replaces the table
  body, `table_view.js` reapplies the current column visibility state to the
  new data rows. Add separator rows are excluded from positional column
  hiding so their handlers remain visible.
- The rows filter also refreshes against the current table body after Turbo
  replacement: it rebuilds the available row types, reapplies hidden types
  from storage, and binds its controls to the new `tbody`.
- Added Turbo refresh of `table-content-body`, TOC refresh, feedback marker,
  and post-create viewport positioning without opening an editable field.
- Added focused end-to-end coverage for:
  - create requirement before first row;
  - create requirement as child of a section;
  - block while sorted;
  - block while row types are hidden;
  - show and clear simultaneous sorting and row-filter blockers;
  - preserve the open menu position across both blocker resets;
  - preserve an active edit row and edit state during sorting;
  - confirm that row filtering completes the active cell's existing
    outside-click lifecycle without preserving its row position;
  - preserve the Add menu top-left position in the newly created row;
  - confirm newly created nodes do not open an edit field;
  - disable required `SingleChoice` node types.
- Updated `test_cases.md` with the complete Add Node matrix. Existing coverage
  is marked `[x]`; missing placement, grammar-default, failure, explicit
  post-create edit-mode, and empty-state checks remain marked `[ ]`.

## Verification

- `python -m py_compile strictdoc/server/routers/main_router.py strictdoc/export/html/generators/view_objects/document_screen_view_object.py`
- `pytest -q tests/unit/strictdoc/export/html/test_html_templates.py`
- `invoke test-end2end --focus add_table_node_blocked_when_sorted
  --headless`: 1 passed.
- `invoke test-end2end --focus add_table_node --headless`: 5 passed.
- `invoke test-end2end --focus view_table_document_column_visibility
  --headless`: 2 passed.
- `invoke test-end2end --focus view_table_document_row_visibility_toggle
  --headless`: 1 passed.
- `invoke test-end2end --focus edit_table --headless`: 30 passed.
- `node --check strictdoc/export/html/_static/table_view.js`
- `node --check strictdoc/export/html/_static/table_view_edit.js`
- `git diff --check`
- `invoke lint-ruff`
- `invoke lint-mypy`: success on 268 source files.

## Next step

- Stop for user review and an intermediate commit.
