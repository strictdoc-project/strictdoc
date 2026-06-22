# Autocomplete: already-selected values are re-suggested (MultipleChoice/Tag)

## WHAT

In MultipleChoice/Tag fields (comma-separated multi-value autocomplete), a
value that is already present in the field must not be insertable a second
time via the autocomplete dropdown.

- A value already present in the field (whether it's the only value typed
  so far with no trailing comma, or it's the last, fully-typed
  comma-separated segment) must stay visible in the dropdown, but visually
  marked as already selected ("подсвечено").
- Selecting it again (click or keyboard) must not insert a duplicate / must
  not change the field's value.
- Out of scope: detecting which value the user clicked on based on cursor
  position (i.e. distinguishing "clicked on the in-progress query segment"
  vs. "clicked on an earlier, already-committed value" elsewhere in the
  text). The dropdown's query is always derived from the segment after the
  last comma in the whole field text, regardless of where the user actually
  places the cursor — this is a separate, harder problem and is
  deliberately not addressed here.

## WHY

A Set-like field (Tag/MultipleChoice) should not let the same value be
picked twice via autocomplete. Right now nothing prevents it:

- The server (`get_autocomplete_field_results` in
  `strictdoc/server/routers/main_router.py`) only excludes values found in
  `parts[:-1]` — the comma-segments *before* the last one. The last
  segment is always treated as "still being typed" and is matched against
  itself, even once it's a complete, exact match for an existing option.
- Concretely:
  - If the field currently has a single value with no trailing comma yet
    (e.g. `Tag1`), re-opening the dropdown (click/focus) shows `Tag1`
    itself as a suggestion, even though it's already the field's value.
  - After adding a comma and typing a second value in full (e.g.
    `Tag1, Tag2`), re-opening the dropdown shows `Tag2` (the last,
    already fully-typed value) as a suggestion again — regardless of
    where in the text the user clicks, because the query is always derived
    from the whole field text's last comma-segment, not from cursor
    position.

This is confusing: the user sees a value they already picked offered again
as if it were a fresh, separate choice.

This is the classic "multi-select combobox / tag input" duplicate-selection
problem. The standard UX pattern (GitHub labels, Gmail "To:" field,
MUI/Ant/Headless-UI multi-select, etc.) is to keep already-selected values
visible in the list but visually marked and inert — not to hide them, and
not to let them be re-inserted.

## HOW

> Note: during implementation it turned out a JS controller change *was*
> required after all (see step 0 below) — the click handler was discarding
> the current field text entirely for MultipleChoice/Tag fields, which is
> the actual root cause of the most commonly reported case (re-opening the
> dropdown via click right after picking a value). This was confirmed with
> the user before implementing.

Reuse the same `aria-disabled` pattern already used for the "No matches
found" placeholder: `replaceResults()` in
`strictdoc/export/html/_static/controllers/autocompletable_field_controller.js`
already excludes `aria-disabled` rows from `this.options` (keyboard nav,
`selectText()`, `onResultsClick` → `commit()`) for free, via the existing
`optionSelector` constant (`[role='option']:not([aria-disabled])`).

### 0. JS controller — `autocompletable_field_controller.js` (click handler)

The click handler used `minLengthValue == 0 ? "" : innerText.trim()` as the
query for *all* autocompletable fields (TAG/MultipleChoice/SingleChoice all
use `autocomplete_len="0"`, see `row_with_text_field.jinja`). For
MultipleChoice/Tag fields this meant a click **always** sent an empty
query, discarding any already-typed value and its comma-context — so the
server's existing `parts[:-1]` exclusion never had anything to exclude on
click. This is the actual cause of "select Tag1, click the field again
(no comma typed) → Tag1 is offered again."

Fix, extracted into `buildClickQuery()`:
- SingleChoice (`!multipleChoiceValue`): unchanged, always `""` (click acts
  like a `<select>` dropdown showing the full list).
- MultipleChoice/Tag, field empty or already ending with `,`: send the
  current text as-is (same as typing).
- MultipleChoice/Tag with a complete value and **no** trailing comma:
  clicking to browse more options is equivalent to the user having just
  typed a separating comma. We actually **insert** `", "` into the
  contenteditable (not just into the query string) — otherwise `commit()`
  later re-splits the *real* field text on commas, finds none, and
  overwrites the existing value instead of appending the new one. The
  cursor-move logic shared with `commit()` was extracted into
  `moveCursorToEnd()` to avoid duplicating it.

### 1. Server — `strictdoc/server/routers/main_router.py`

In `get_autocomplete_field_results`, MULTIPLE_CHOICE/TAG branch:

- Keep computing `already_selected` from `parts[:-1]` (unchanged).
- Additionally treat the **last segment** (`last_part`) as "already
  selected" too, but only on an **exact** (not substring) case-insensitive
  match against an option. This single extra check covers both reported
  cases (no-comma single value; fully-typed last value after a comma).
- Build `resulting_values` as a list of `(value, is_selected: bool)` pairs
  instead of plain strings, where `is_selected` is true if the value
  (case-insensitive) is in `already_selected` or exactly equals
  `last_part`.
- Do **not** drop already-selected values from the list — keep them so
  they're still rendered (per the "highlight, don't hide" requirement).

### 2. Template —
`strictdoc/export/html/templates/autocomplete/field/stream_autocomplete_field.jinja.html`

For each `(value, is_selected)`, render:

```html
<li class="autocompletable-result-item{% if is_selected %} autocompletable-result-item_selected{% endif %}"
    role="option"
    {% if is_selected %}aria-disabled="true"{% endif %}
    data-autocompletable-value="{{ value }}">{{ value }}</li>
```

### 3. CSS — `strictdoc/export/html/_static/form.css`

Add `.autocompletable-result-item_selected` — muted color + `cursor:
default`, matching the visual language of `.autocompletable-result-item_no-results`.

### 4. Tests

Added
`tests/end2end/screens/document/create_requirement/_Tag/create_requirement_Tag_field_autocomplete_no_duplicates/`:
opens a requirement whose TAGS field already has `Tag1` (document also has
`Tag2` used elsewhere, so the dropdown has something else to legitimately
offer), clicks the field, asserts no `<li data-autocompletable-value="Tag1">`
is present in the results, then sends Arrow-Down + Enter and asserts
`Tag1` isn't duplicated in the field's text.

New helpers:
- `Form.assert_autocomplete_no_duplicate_on_click()` /
  `Form_EditRequirement.assert_field_autocomplete_no_duplicate_on_click()`
  (click case).
- `Form.assert_autocomplete_no_results()` /
  `Form_EditRequirement.assert_field_autocomplete_no_results()` were added
  earlier for the empty-state task and are reused/adjacent here.

### Scope notes

- Scoped to the MULTIPLE_CHOICE/TAG branch only — SingleChoice fields have
  Set-of-one semantics where re-showing the current value is normal (e.g.
  picking a different one), so they're unaffected and out of scope.
- Cursor-position-aware filtering (clicking on an earlier value vs. the
  in-progress segment) is explicitly out of scope, per the WHAT section.
