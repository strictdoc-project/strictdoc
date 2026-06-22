# Fix the autocomplete display for empty results

## WHAT

When autocomplete cannot find any results to display, the message “No matches found” should appear.

## WHY

Right now, nothing is displayed at all. This is bad UX.

## HOW

The empty-state message is rendered entirely client-side.

Test case:

The test verifies that when a user enters a query into the TAGS autocomplete
field that has no matching options, the dropdown displays a disabled
“No matches found” entry and that this entry cannot be selected via keyboard
navigation.

Test steps:

* Open a test document containing a requirement that already has the tag Tag1.
* Open the requirement edit form.
* Enter a guaranteed non-existent tag (ZzZ_no_such_tag) into the TAGS field.
* Wait for the autocomplete dropdown and verify that it contains
a aria-disabled="true" entry with the text “No matches found”.
* Record the current field value, press Arrow Down and Enter (as if selecting
a normal option), and verify that the field value remains unchanged, confirming
that the placeholder entry cannot be selected.
* Close the form using “Cancel” without saving.
* Verify that the sandbox matches the original files, confirming that the
document was not modified.

### Implementation notes

- Root cause: when the server returns zero matches, the autocomplete
  fragment is an empty string. `AutoCompletable.replaceResults()` always
  calls `open()` regardless of result count (`this.options` is an array,
  which is always truthy), so the dropdown opened with zero `<li>` children
  and rendered nothing visible.
- `replaceResults()` detects an empty/whitespace-only fragment and
  injects a single placeholder row instead:
  `<li class="autocompletable-result-item autocompletable-result-item_no-results" role="option" aria-disabled="true">No matches found</li>`.
- The placeholder reuses the existing `optionSelector` filter
  (`[role='option']:not([aria-disabled])`): `aria-disabled="true"` means it
  is automatically excluded from `this.options`, so keyboard navigation
  (arrow keys, Tab, Enter → `commit()`) and mouse click on it are no-ops,
  with no extra guard code required.
- `strictdoc/export/html/templates/components/form/field/autocompletable/index.jinja`:
  gets `aria-live="polite"` to the results `<ul>` so screen readers announce
  the "No matches found" message when it's injected.
- `strictdoc/export/html/_static/form.css`:
  `.autocompletable-result-item_no-results` gets a modifier class (muted color,
  italic, default cursor) for the placeholder row.

- e2e test:
  `tests/end2end/screens/document/create_requirement/_Tag/create_requirement_Tag_field_autocomplete_no_matches/`,
  using a new helper `Form.assert_autocomplete_no_results()` /
  `Form_EditRequirement.assert_field_autocomplete_no_results()` that asserts
  the placeholder is shown and that Arrow-Down + Enter does not change the
  field's content.
