# Per-tab error badge must count invalid fields, not error messages

## WHAT

- In the node-edit popup form (tabs: `Fields`, `Relations`, `Comments`), each
  tab with at least one invalid field shows a red numeric badge.
- The badge must show the number of **distinct fields** on that tab that have
  at least one validation error.
- It currently shows the total number of validation **error messages** on
  that tab, which over-counts whenever a single field accumulates more than
  one error message (e.g. the `UID` field can carry up to three messages at
  once: uniqueness, "requires an UID because it has parent relations",
  "renaming with parent/child relations not supported").
- Individual field-level error display is out of scope and already correct:
  each error message must keep rendering in its own `<sdoc-form-error>` tag
  under its field, one tag per message, even when a field has several.
- Applies uniformly to all fields/tabs, not just `UID`.

### Test case

- Trigger a validation failure where one field (e.g. `UID`) ends up with two
  error messages and another field on the same tab (e.g. `STATEMENT`) ends
  up with one error message.
- The tab badge must read `2` (two invalid fields), not `3` (three error
  messages).
- Both `UID` error messages must still each render in their own
  `<sdoc-form-error>` tag.

## WHY

- The badge is meant to tell the user how many fields need attention on a
  tab, so they know how much work is left before the form can be submitted.
- Reporting the message count instead misleads the user: e.g. a badge
  reading "3" for what is actually one problem field (with 3 stacked
  messages) plus one other field overstates the number of things to fix,
  and doesn't match the number of fields actually shown as invalid.

## HOW

- The count is currently computed entirely client-side, in
  `strictdoc/export/html/_static/tabs.js`, via
  `contentEl.querySelectorAll('sdoc-form-error').length` — one entry per
  `<sdoc-form-error>` DOM node, i.e. per error message, not per field.
  The badge itself is pure CSS
  (`strictdoc/export/html/_static/element.css`), driven by the
  `data-errors` attribute that `tabs.js` sets on `<sdoc-tab>`.
- Field-level error messages are rendered by the row/field partials under
  `strictdoc/export/html/templates/components/form/...`
  (e.g. `row/row_with_text_field.jinja`, `field/contenteditable/index.jinja`,
  `field/autocompletable/index.jinja`, `row/row_with_relation.jinja`,
  `row/row_with_comment.jinja`, `row/row_uid_with_reset/frame.jinja`), each
  looping over its own field's error list and emitting one
  `<sdoc-form-error>` per message — this part is unchanged.
- Fix direction (to be confirmed during implementation): count distinct
  error-owning field containers per tab instead of raw `<sdoc-form-error>`
  nodes — e.g. in `tabs.js`, count elements that carry a field-level wrapper
  attribute/class and have at least one `sdoc-form-error` descendant, rather
  than counting the `sdoc-form-error` descendants themselves. No Python
  changes appear necessary since error grouping by field name already
  exists server-side in `strictdoc/server/error_object.py`
  (`ErrorObject.errors: Dict[str, List[str]]`).
- No existing automated test asserts on the badge's `data-errors` value.
  Add end2end coverage for a field with multiple stacked error messages
  (e.g. the `UID` "must be unique" + "parent relations" combination, or a
  synthetic case) confirming the badge equals the number of invalid fields;
  extend `tests/end2end/helpers/form/form.py` with an assertion helper for
  the tab badge count if none exists.
