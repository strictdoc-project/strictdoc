# Table View: Delete Node

## WHY

Table edit mode already supports changing fields and adding nodes, but deleting
a node still requires switching to Document view. Node deletion should be
available from the same table row where the user is editing the document.

The feature must reuse the existing deletion rules, validation, and
confirmation behavior. It must not introduce a second deletion model or bypass
the checks used by Document view.

## WHAT

In Table edit mode, the `TYPE` cell of each deletable node exposes the shared
delete button from `components/button_inline/delete.jinja`.

The behavior is:

- the `TYPE` cell is rendered by a feature-local partial so its layout can
  contain both the node type and the delete action;
- the delete action is visible only in Table edit mode;
- clicking the action opens the same confirmation modal pattern as Document
  view;
- cancelling the modal leaves the table unchanged;
- confirming deletes the node and refreshes the Table body and TOC through
  Turbo;
- Table edit mode remains active after the refresh;
- nodes rejected by `can_delete_node()` expose a visible disabled delete
  action, consistently with Document view. `can_delete_node()` returns
  `False` in three cases: the node's parent document has `autogen: True`;
  the node itself is managed by source code (`is_managed_by_source_code()`);
  or the subject is a document with `autogen: True`;
- validation errors are shown in the confirmation modal; when errors are
  present the Confirm button in the modal is rendered disabled so the user
  cannot submit an invalid deletion request;
- a direct confirmed request (`confirmed=True`) that fails server-side
  validation must return a `422` response, never a `5xx`.

CSS changes must be limited to the minimum layout and edit-mode visibility
rules needed to place the button in `.content-view-td-type`.

## HOW

Add a Table-local partial for `.content-view-td-type`. The partial receives the
node and renders its type together with `components/button_inline/delete.jinja`,
including the node MID and context document MID in the action URL.

Use the existing Turbo and `modal_controller.js` setup already loaded by Table
view. The Table delete action shall reuse `DeleteRequirementCommand` and the
traceability index deletion checks.

The Table response must be local to Table view:

- the initial request updates `#confirm` with the shared confirmation modal;
- the confirmed request performs deletion and replaces
  `#table-content-body`;
- the response also updates the TOC and clears `#confirm`.

The `stream_confirm.jinja` template must render the Confirm button with the
`disabled` attribute whenever `errors` is non-empty. This prevents the user
from submitting a confirmed deletion request that the server would reject.

The confirmed deletion endpoint (`confirmed=True`) must also guard against
`5xx` responses: if `DeleteRequirementCommand.perform()` raises a validation
exception, the handler must catch it and return `422`, not propagate it as an
unhandled server error.

Do not change the Document view deletion behavior as part of this feature.

## Verification Requirements

Automated coverage must verify:

- the delete action is hidden outside Table edit mode and visible in edit mode;
- cancelling confirmation keeps the node and table unchanged;
- confirming deletes a requirement row and persists the deletion;
- confirming deletes a section row and preserves valid document structure;
- successful deletion refreshes the Table body and TOC;
- Table edit mode remains active after deletion;
- a node rejected by `can_delete_node()` has a visible disabled delete action;
- a validation failure is shown in the modal and does not delete the node;
- the Confirm button is disabled in the modal when validation errors are
  present, so a second click cannot reach the server;
- a direct confirmed request sent when validation fails returns `422`, not
  `5xx`.

Required checks:

- `pytest -q tests/unit/strictdoc/export/html/test_html_templates.py`
- `invoke test-end2end --focus delete_table_node --headless`
- `invoke test-end2end --focus edit_table --headless`
- `git diff --check`
- `invoke lint-ruff`
- `invoke lint-mypy`
