# Editable grammars imported via IMPORT_FROM_FILE

## WHAT

Removes the "Editing imported grammar files is not implemented yet."
placeholder that blocked the "Edit grammar" screen for any document whose
`[GRAMMAR]` block says `IMPORT_FROM_FILE: ...` instead of declaring
`ELEMENTS:` inline, and makes saving through that screen actually persist —
by writing to the referenced `.sgra` file, not the `.sdoc`.

All three eurobot documents (`Eurobot_Requirements.sdoc`,
`Eurobot_Rules.sdoc`, `Eurobot_Tests.sdoc`) use `IMPORT_FROM_FILE`, so this
was blocking every one of them, including the field-type/choice-options
editor added in `20260905_grammar_editor_choice_options` — that editor
worked, it just had no way to be reached for these documents.

## WHY

Direct trigger: the user asked how to add a new value to `TARGET_REVISION`'s
`C1`/`C2` choices from the UI. The editor to do that already existed; the
"Edit grammar" screen's placeholder was in the way of reaching it.

The placeholder turned out not to be just a UI gate: `SDWriter` never
serialized a grammar's `ELEMENTS:` list anywhere once `import_from_file` was
set — it only ever wrote `IMPORT_FROM_FILE: @xxx` back into the `.sdoc`. So
removing the placeholder alone would have silently discarded any edit
instead of showing an error; the write side needed the missing piece before
the UI gate could come down.

## HOW

**Resolving the alias/filename to a real path.**
`TraceabilityIndexBuilder.create()` already resolves `IMPORT_FROM_FILE`
once per project build (an `@alias` through `project_config.grammars`; a
bare filename relative to the importing document's own directory) — that
logic moved into `strictdoc/core/grammar_file_resolver.py`
(`resolve_grammar_file_relative_path`/`resolve_grammar_file_full_path`), and
`TraceabilityIndexBuilder` now calls it too, so the read side (index build)
and the new write side (saving an edit) can never resolve the same
declaration to two different files.

**Serializing a grammar to `.sgra` text.** The exact text a standalone
`.sgra` file needs already existed, inlined in `SDWriter.write_with_fragments`.
Extracted into `SDWriter.write_grammar_elements()` (the `ELEMENTS:` body,
reused by both the inline-grammar path and the new one) and
`write_grammar_file_content()`/`write_grammar_to_file()` (the full
`[GRAMMAR]\nELEMENTS:...` a `.sgra` file is, and writing it to disk).

**The critical distinction the fix has to respect**: node *content*
(STATEMENT, TITLE, field values) always lives in the `.sdoc`, regardless of
where the grammar *structure* comes from — `write_document_to_file`, the
function every node-edit endpoint calls, keeps writing the `.sdoc`
unconditionally. The new "write to the `.sgra` instead" behavior lives only
in a new `write_grammar_change_to_file` helper, called only by the two
grammar-*structure*-editing endpoints
(`document__save_grammar`/`document__save_grammar_element` in
`main_router.py`) in place of their old `write_document_to_file(document)`
call, branching on `document.grammar.import_from_file`.

**Two write-side bugs fixed alongside this, since they only bite once this
path is reachable**: `GrammarFormObject.create_from_request` hardcoded
`imported_grammar_file=None` (fixed: the router sets it from the document
it already has, right after constructing the form object — no need to
round-trip it through the posted form); `UpdateGrammarCommand.perform()`
built a fresh `DocumentGrammar` without passing `import_from_file` through
(fixed: one added keyword argument). Either bug alone would have silently
turned an imported grammar into an inline one on save, dropping
`IMPORT_FROM_FILE` from the `.sdoc` and expanding `ELEMENTS:` into it
instead.

**UI**: `components/grammar_form/index.jinja`'s gate is gone — the form
always renders. In its place, a small notice appears when the grammar is
imported, naming the resolved file (e.g.
`eurobot_requirements_grammar.sgra`, not the raw `@eurobot_requirements`
alias — `GrammarFormObject.resolved_grammar_file_path`), so it's never a
surprise which file gets written.

**Multiple documents sharing one `.sgra` file**: not eurobot's case today
(each of its three `.sgra` files has exactly one importer — see
`eurobot/strictdoc_config.py`'s own comment), but `IMPORT_FROM_FILE` doesn't
prevent it, and a parent/fragment pair sharing one grammar file is an
existing, tested pattern elsewhere in this repo. The save path deliberately
does *not* inhibit the file watcher for the `.sgra` it writes (unlike the
`.sdoc` inhibit `write_document_to_file` already does) — left alone, the
watcher's existing full-project rebuild picks up the change and correctly
refreshes every document importing that file, not just the one being
edited, reusing logic that already exists rather than hand-rolling a
synchronous multi-document refresh. The one visible side effect: the tab
that saved is itself a connected client, so shortly after its own
turbo-stream update it gets one extra, harmless full-page refresh.

### Testing

- `tests/unit/strictdoc/core/test_grammar_file_resolver.py`: alias and
  bare-filename resolution.
- `tests/unit/strictdoc/backend/sdoc/test_sdwriter_grammar_file.py`:
  `write_grammar_file_content()` matches a real `.sgra` fixture byte for
  byte and round-trips through the reader.
- `tests/unit_server/strictdoc/server/24_edit_imported_grammar/`: real
  HTTP saves against a running app — editing a field writes the `.sgra` and
  leaves the `.sdoc` untouched; a normal node content edit still writes the
  `.sdoc` (the content-vs-structure regression guard); the element-list
  save (`document__save_grammar`) has the same fix; a grammar shared by two
  documents propagates to both, checked via a fresh
  `TraceabilityIndexBuilder.create()` (what the watcher's rebuild does)
  rather than real filesystem-watcher timing.
- `tests/end2end/screens/document/view_document/_grammar_from_file/`:
  the existing test that asserted the placeholder now asserts the form is
  editable instead; a new case drives the field-type/options editor on an
  imported grammar end to end and checks both files on disk via
  `expected_output/`. Like the previous task's e2e test, this repo's
  sandbox has no Selenium/Playwright install, so this was written and
  manually equivalent-verified through direct HTTP calls, but not run
  through the actual e2e suite here.
- Manually verified against a scratch copy of the real `eurobot/` project
  (not the tracked files): the placeholder is gone on
  `Eurobot_Requirements.sdoc`, the notice names
  `eurobot_requirements_grammar.sgra`, and saving a `D1` addition to
  `TARGET_REVISION` produces `SingleChoice(C1, C2, D1)` in that file while
  `Eurobot_Requirements.sdoc` stays byte-identical.

### Known limitation

Removing an option that existing nodes already use is not retroactively
validated or migrated — unchanged from before this task, and from how a
hand-edited `.sgra` file already behaves.

Does not touch any `eurobot/*.sgra` or `eurobot/*.sdoc` content — this adds
the mechanism to edit `TARGET_REVISION`'s options via the UI; it does not
add a `D1` option for the user.
