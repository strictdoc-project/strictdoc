# Restore-UID button on "renaming UID with relations" validation error

## WHAT

- When a user edits a requirement's `UID` field and submits the form while
  the requirement still has parent or child relations, validation currently
  rejects the change with an inline error:
  > Not supported yet: Renaming a requirement UID when the requirement has
  > parent requirement relations. For now, manually delete the relations,
  > rename the UID, recreate the relations.
  (a sibling message exists for child relations).
- Today the form re-renders with the `UID` field still showing the new
  (rejected) value the user typed, alongside the error message, with no way
  to get back to the previous, valid UID short of closing the form.
- When this specific validation error fires, show a "restore" button next
  to the `UID` field, in `sdoc-form-row-aside`, next to where the existing
  reset button (`data-action-type="reset"`, tooltip "Generate default UID")
  lives for the empty-UID case. Clicking it puts the requirement's original
  UID (the value it had when the form was opened) back into the field, in
  place, without submitting or closing the form, and clears the now-stale
  validation error(s) shown for that field.
- This applies to both the parent-relations and child-relations variants of
  this error.
- The existing "reset" button's tooltip was renamed from "Reset UID to
  default" to "Generate default UID": once both buttons can appear side by
  side (empty UID + relations-blocked rename), "Reset" read as too close in
  meaning to the new "Restore UID" even though it does something different
  (invents a new auto-numbered UID vs. bringing back the prior one).
- Out of scope: changing the underlying rule that UID renaming is blocked
  while relations exist; any change to how relations themselves are
  deleted/recreated; the reset button's behavior itself (unrelated — it
  generates a new auto-numbered UID for an empty field, it does not
  restore a prior value; only its tooltip text changed).

### Test case

- Open the edit form for a requirement that has a parent relation.
- Change `UID` to a new value and submit.
- The form re-renders with the parent-relations error message, the `UID`
  field still showing the rejected value, and a restore button next to it.
- Clicking the restore button puts the requirement's original UID back into
  the field (in place, no submit) and removes the error message(s) shown
  for that field.
- Same behavior for a requirement with a child relation and the
  child-relations error message.
- The restore button must not appear on an otherwise-normal edit (no such
  error).
- Same behavior when the UID was cleared to empty (not just retyped) while
  relations exist — a different template/code path (see HOW).

## WHY

- The error message tells the user the rename cannot proceed as submitted,
  but the form still shows the rejected new UID as if it were accepted,
  which is misleading and leaves the field in a value that cannot actually
  be saved without further action (deleting relations first).
- A restore action lets the user get back to a known-good value without
  closing the form (losing the rest of their in-progress edits) or having
  to remember/retype the original UID themselves.

## HOW (implemented)

- `strictdoc/export/html/form_objects/requirement_form_object.py`:
  `RequirementFormObject.__init__` gained
  `self.uid_rename_blocked_by_relations: bool = False`; `validate()` sets
  it to `True` at both `add_error("UID", "Not supported yet: ...")` call
  sites (parent-relations branch and child-relations branch). The `UID`
  field's `field_value` itself is left untouched (still shows what the
  user typed) — restoring is a manual, explicit user action, not implicit.
- `strictdoc/export/html/templates/screens/document/document/frame_requirement_form.jinja`:
  passes `text_field_row_context.existing_requirement_uid =
  form_object.existing_requirement_uid` and
  `text_field_row_context.uid_restore_available =
  form_object.uid_rename_blocked_by_relations` into the single-line field
  loop (harmless for non-UID fields, only read by the UID row).
- `strictdoc/export/html/templates/components/form/row/row_with_text_field.jinja`:
  `row_right` block now renders an `<a data-js-restore-field-action
  data-restore-value="{{ existing_requirement_uid }}"
  data-testid="restore-uid-field-action">` when
  `field.field_name == "UID"` and `uid_restore_available` is true.
- `strictdoc/export/html/templates/components/form/row/row_uid_with_reset/frame.jinja`:
  same restore button, added next to the existing reset button. Needed
  separately: when the UID is cleared to an **empty** string (not renamed
  to another value), `frame_requirement_form.jinja` renders this template
  instead of `row_with_text_field.jinja` (the `field_.field_value == ""`
  branch) — an empty UID with parent/child relations still triggers
  `uid_rename_blocked_by_relations` (alongside the separate "must have a
  UID" error), so the restore button has to exist on this code path too.
  Missed in the first pass; found via manual testing, not by the e2e
  tests below (they only covered the "rename to another value" path).
- `strictdoc/export/html/templates/icons/ico16_restore.svg`: new icon —
  a single undo-style arrow, using the same top arc as `ico16_reset.svg`'s
  first path (`M5,4 C8.5,1.5 13,4 13,9`) but with a custom arrowhead
  attached at the arc's start (left/top) instead of its end, so the arrow
  reads as "go back" rather than "go forward".
- `strictdoc/export/html/_static/restorable_field.js`: new vanilla-JS
  delegated click listener (same pattern as `deletable_field.js` /
  `movable_field.js`) for `[data-js-restore-field-action]`. Pure
  client-side: no server round-trip, since the original value is already
  embedded in the button's `data-restore-value` at render time. Sets both
  the visible `[data-js-editable-field]` element's `textContent` and its
  hidden mirror input's `.value` (mirroring what `editable_field.js` keeps
  in sync on user typing), and removes all `<sdoc-form-error>` elements
  inside the field's `sdoc-form-row` — the errors described why the
  rejected value was invalid, which no longer applies once restored.
- `strictdoc/export/html/templates/screens/document/document/index.jinja`:
  registered the new script alongside `deletable_field.js` /
  `movable_field.js`.
- `strictdoc/export/html/templates/components/form/row/row_uid_with_reset/frame.jinja`:
  the pre-existing reset button's `title` changed from
  "Reset UID to default" to "Generate default UID" (text only — same
  `data-testid="reset-uid-field-action"`, same behavior).
- Tests extended:
  `tests/end2end/helpers/screens/document/form_edit_requirement.py` gained
  `assert_uid_field_has_restore_button`,
  `assert_uid_field_has_not_restore_button`, `do_restore_uid_field`
  (mirroring the existing `..._reset_button`/`do_reset_uid_field` helpers).
  `tests/end2end/helpers/form/form.py` gained `assert_error_not_present`.
  `tests/end2end/screens/document/_cross_cutting/RELATIONS/update_node/update_requirement_renaming_uid_when_parent_links_exist/test_case.py`
  and the `..._when_child_links_exist` sibling now also assert the button
  appears, click it, assert the field shows the original UID again, and
  assert the error message is no longer present.
  The parent-links test additionally covers the empty-UID variant (clear
  the field entirely instead of typing a replacement), which is what
  caught the `row_uid_with_reset/frame.jinja` gap above.
- Verified against manual reverts (stashing one fix file at a time,
  including just the error-clearing line in `restorable_field.js` and just
  the `row_uid_with_reset/frame.jinja` addition): every extended e2e test
  fails on the corresponding pre-fix code and passes with the fix.
