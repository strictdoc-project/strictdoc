# Grammar editor: editable field type and choice options

## WHAT

Extends the "Edit Grammar Element" screen
(`strictdoc/export/html/form_objects/grammar_element_form_object.py` and
`strictdoc/export/html/templates/components/grammar_form_element/row_with_custom_field/index.jinja`)
so a custom field can have its type changed between `String`, `SingleChoice`,
`MultipleChoice`, and `Tag`, and — for the two choice types — its option
list edited as one comma-separated text field (e.g. `C1, C2, D1`).

This also fixes a latent bug in the same code path: saving that screen
previously rebuilt every field as a plain `String` regardless of its actual
type, so saving the form at all — even leaving every field untouched — would
have silently turned any `SingleChoice`/`MultipleChoice`/`Tag` field into a
`String` and thrown away its declared options.

## WHY

The user asked how to add or edit revisions from the UI: `REQUIREMENT`'s
`TARGET_REVISION` field (declared in `eurobot/eurobot_grammar.sgra` and
`eurobot/eurobot_requirements_grammar.sgra`) only ever offers `C1`/`C2`, and
there was no way to grow that list without hand-editing the `.sgra` file.

There is no dedicated "revision" concept anywhere in the code —
`TARGET_REVISION` is an ordinary `SingleChoice` grammar field, the same
mechanism `STATUS` uses, and per-node editing (picking `C1` vs `C2` on a
given requirement) already worked before this change, through StrictDoc's
generic autocomplete widget. The missing piece was managing the *declared
option list itself*, and the grammar editor — the natural place for that —
had no notion of field type or options at all: every field it read was
treated as, and written back as, a `String`.

Fixing `convert_to_grammar_element` to preserve the original field's type
happens in the same change, not separately, because it is the same method
that needed to gain type/option awareness to support editing them in the
first place.

## HOW

**`GrammarFormField`** gained two fields: `field_type` (one of
`RequirementFieldType.STRING`/`SINGLE_CHOICE`/`MULTIPLE_CHOICE`/`TAG`) and
`field_options` (a comma-separated string, empty unless the type needs it).
`create_from_grammar_field` now reads both off the underlying
`GrammarElementField` instead of assuming `String`.

**`convert_to_grammar_element`** now branches on `field.field_type` and
builds the matching `GrammarElementField` subclass, parsing `field_options`
into a list (trimmed, empty entries dropped) for the two choice types. This
is the fix for the data-loss bug described above.

**`validate()`** gained one rule: a `SingleChoice`/`MultipleChoice` field
must resolve to at least one option after parsing, or the form reports an
error on that field instead of silently saving an empty choice list.

**The template** gained a `<select>` for field type (mirroring the existing
relation-type `<select>` in `row_with_relation/index.jinja`) and a
`contenteditable` singleline input for options (mirroring the existing field
name/human title inputs in the same row), both wired to the new
`GrammarFormField` getters. Reserved fields (`UID`, `TITLE`, `STATEMENT`,
`RATIONALE`, `COMMENT`) are unaffected — they are rendered by a separate
template and stay implicitly `String`.

Nothing else needed to change: the `.sgra` parser/writer already handled all
four field types correctly (that's why `TARGET_REVISION` read as
`SingleChoice(C1, C2)` before this change), and the per-node
autocomplete/validation path (`_validate_choice`,
`GET /autocomplete/field`) already reads options generically off the
grammar, with no hardcoded field names.

### Known limitation

Removing an option that existing nodes already use is not retroactively
validated or migrated. A node keeps its old value until someone edits that
node's field again, at which point the existing per-node validation rejects
the now-undeclared value. This matches today's behavior when the option
list is edited by hand in the `.sgra` file — not a regression, and not
something this change improves.

### Testing

- `tests/unit/strictdoc/export/html/form_objects/test_grammar_element_form_object.py`:
  plain-object tests for `GrammarFormField`/`GrammarElementFormObject` —
  read/write round-tripping for each field type, whitespace handling in the
  options list, and the new empty-options validation rule.
- `tests/unit/strictdoc/export/html/form_objects/test_grammar_element_form_object_sdoc_round_trip.py`:
  the same behavior through the real `.sdoc` reader, writer, and Jinja
  template, using a `TARGET_REVISION`-shaped fixture — an untouched save
  keeps `SingleChoice(C1, C2)` intact, and appending an option produces
  `SingleChoice(C1, C2, D1)` in the written file and in the rendered form.
- `tests/end2end/screens/document/edit_document_grammar_element/edit_grammar_field_set_single_choice_options/`:
  a browser-driven case covering the same scenario end-to-end (this repo's
  sandbox has no Selenium/Playwright install, so this one could not be run
  here — see the report-back notes for the exact commands to run it
  elsewhere).

Does not touch `eurobot/eurobot_grammar.sgra`,
`eurobot/eurobot_requirements_grammar.sgra`, or any `.sdoc` content —
`TARGET_REVISION`'s declared options stay `C1, C2`. The point of this task
is that a mentor can now add e.g. `D1` themselves from the UI, not that this
task adds it for them.
