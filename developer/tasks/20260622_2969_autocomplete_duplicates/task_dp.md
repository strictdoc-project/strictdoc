# MultipleChoice/Tag field: deduplicate existing values when opening the edit form

## WHAT

When a requirement's MultipleChoice/Tag field already contains duplicate
values (e.g. `Tag1, Tag1`), opening that field for editing must show it
with duplicates already removed. No server-side validation or
save-blocking is required — if the user saves as-is, the document is
cleaned up as a side effect of the normal save.

This requirement applies to **both** editing surfaces, as they are
implemented and tested independently of each other:
- the modal requirement-edit form;
- the table-view inline cell editor.

## WHY

[[task_ac]] prevents *new* duplicates from being inserted via autocomplete,
but does nothing for values that are already duplicated in the document
(typed by hand, edited outside the UI, or present before that fix existed).
There is currently no code path that detects or cleans up duplicates in
already-saved field values.

## HOW

There are **two** independent code paths that load an existing field's
value for editing, matching the two surfaces from WHAT — both need the fix:

1. `strictdoc/export/html/form_objects/requirement_form_object.py`,
   `RequirementFormField.create_existing_from_grammar_field()` — used when
   opening the modal requirement-edit form
   (`get_edit_requirement` in `main_router.py`).
2. `strictdoc/server/routers/main_router.py`,
   `table__get_node_autocomplete_inline()` (~line 1471) — used when
   entering edit mode on a table-view cell. This reads
   `node.ordered_fields_lookup[field_name][0].get_text_value()` directly,
   completely bypassing `RequirementFormObject`.

Implementation:
- `deduplicate_comma_separated_value()` (public function in
  `requirement_form_object.py`, used from both places): splits a
  comma-separated value, strips each part, drops empty parts, and removes
  case-insensitive duplicates while keeping the order and original casing
  of the first occurrence.
- Applied in (1) to `field_value` only when `grammar_field.gef_type` is
  `MULTIPLE_CHOICE` or `TAG`.
- Applied in (2) to `current_value` only when `is_multiple_choice` is true
  (same two types, already computed there as `is_multiple_choice`).
- `create_from_grammar_field()` (brand-new requirements) and the
  read-only/display-mode cell rendering (`field_name in
  node.ordered_fields_lookup` branch around main_router.py:2131, used to
  render the cell when *not* editing) are intentionally left untouched —
  no existing value to deduplicate in the first case, and the task is
  scoped to the *edit* experience, not to silently changing what's
  displayed for unsaved/unedited data.
- A code comment at each call site explains why the dedup happens there
  (existing documents may predate the autocomplete fix or be hand-edited).

### Tests

- Unit tests for `deduplicate_comma_separated_value()` covering: simple
  duplicates, different casing, extra whitespace, empty parts, single
  value, empty value.
- Verified manually against a running server (both
  `/actions/document/edit_requirement` and
  `/actions/table/get_node_autocomplete_inline`) with a field value of
  `Tag1, Tag1, Tag2` — both now return `Tag1, Tag2`.
- Existing e2e tests for table-cell autocomplete
  (`edit_table_cell_single_choice`, `edit_table_cell_multiple_choice`)
  re-run, still passing.
