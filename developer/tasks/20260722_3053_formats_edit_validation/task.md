# Validate document path extension against editable formats on document creation

## WHAT

When a user creates a new document via the web UI ("Add Document" on the
project home page), `document_path` validation and file-extension handling
must change as follows:

- Remove the current auto-append-`.sdoc`-if-missing behavior in
  `document_tree__create_document()`
  (`strictdoc/server/routers/main_router.py`). The extension is no longer
  silently added; the user must supply it explicitly as part of
  `document_path`.
- Add a new, separate validation step: `document_path` must end with an
  extension that belongs to one of the project's *editable* formats, i.e. a
  `Format` in `project_config.formats` whose `supports_edit()` is `True`.
  The set of allowed extensions is the union of `supported_extensions()`
  from every such format.
- This "format is allowed" validation is distinct from the existing
  `include_doc_paths` / `exclude_doc_paths` path-filter validation:
  - Different concern: one validates *where* the file may live, the other
    validates *what kind* of file it may be.
  - Different, non-overlapping error message, so the user can tell why the
    save was rejected.
  - Both may fire independently for the same submission (e.g. a path
    outside `include_doc_paths` *and* an unsupported/missing extension).
- The allowed-extensions list must never be hardcoded. It is computed at
  request time from `project_config.formats`, so any format added or
  removed from the project config (now or in the future) is reflected
  automatically in both the validation and the user-facing hint, with no
  further code changes.
- Provide the same dynamically computed extensions list (and/or a
  ready-to-render string) to the "Add Document" form template, to back a
  TIP telling the user which extensions are accepted. The final visual
  design of the TIP will be done separately; the backend should hand the
  template a reasonable placeholder value (list/string of allowed
  extensions) it can render.
- Remove the current decorative `.sdoc` suffix hint
  (`singleline_suffix='.sdoc'` in
  `strictdoc/features/project_index/templates/features/project_index/frame_form_new_document.jinja.html`),
  since it is misleading now that more than one extension can be valid and
  it visually duplicates an extension the user already typed (producing an
  apparent `name.sdoc.sdoc`).

## WHY

Reported bug: entering a document name without an extension and clicking
Save produces the error `Document path is not a valid path according to
the project config's setting 'include_doc_paths': [...]`, even though the
only actual problem is the missing extension. Investigation
(`strictdoc/server/routers/main_router.py:2935-2983`) showed the root
cause: `include_doc_paths`/`exclude_doc_paths` filters run against the raw
`document_path`, and the `.sdoc` extension is only appended afterwards, if
validation already passed. In addition, the UI shows a decorative orange
`.sdoc` hint next to the input that is never merged into the submitted
value, so a user who *does* type `.sdoc` sees a confusing
`name.sdoc.sdoc`.

A minimal fix (move the extension-append earlier) would only paper over
the symptom. The real cause is architectural: StrictDoc's document-edit
path is no longer single-format. `Format.supports_edit()` /
`Format.supported_extensions()` already exist
(`strictdoc/core/format.py`), and both `SDocFormat` (`.sdoc`) and
`MarkdownFormat` (`.md`, `.markdown`) currently report
`supports_edit() == True`; `write_document_to_file()`
(`strictdoc/server/routers/main_router.py:299-325`) already branches on
the file extension to pick the right writer. Silently forcing `.sdoc` onto
every new document is actively wrong in a project that also allows
Markdown documents — it would create a `.sdoc` file when the user asked
for `.md`, with no way to disambiguate. More editable formats are
expected to be added over time, so the create-document validation and
UI hint need to be driven by the live, configured list of editable
formats rather than a hardcoded extension, matching the pattern already
established by the `Format` abstraction (see prior tasks
`20260711_1_format_abstraction`, `20260711_2_connect_import_to_formats`).

## HOW

- Add a helper that computes the allowed extensions for document creation,
  e.g. `ProjectConfig.get_editable_document_extensions() -> List[str]` in
  `strictdoc/core/project_config.py`: iterate `self.formats`, keep formats
  where `format_.supports_edit()` is `True`, extend the result with each
  format's `supported_extensions()`, dedupe while preserving order.
- In `document_tree__create_document()`
  (`strictdoc/server/routers/main_router.py`):
  - Delete the `if not document_path.endswith(".sdoc"): document_path =
    document_path + ".sdoc"` block (currently lines 2982-2983).
  - After the existing `include_doc_paths`/`exclude_doc_paths` checks, add
    a new check: if `document_path` does not end with any extension from
    `project_config.get_editable_document_extensions()`, call
    `error_object.add_error("document_path", ...)` with a message that
    names the allowed extensions and is clearly distinct from the
    path-filter error text (e.g. "Document path must end with one of the
    supported extensions: .sdoc, .md, .markdown." vs. the existing
    "Document path is not a valid path according to ... 'include_doc_paths'").
  - Pass the computed extensions (or a formatted string) into both
    `stream_new_document.jinja.html` (error re-render path) and the
    initial `frame_form_new_document.jinja.html` render, alongside the
    existing `include_doc_paths` context variable.
- Template changes (`frame_form_new_document.jinja.html`): remove the
  `singleline_suffix='.sdoc'` argument; add a TIP block analogous to the
  existing `include_doc_paths` `<sdoc-form-hint>`, driven by the new
  extensions variable. Actual visual/UX polish of the TIP is out of scope
  here and will be done separately.
- Testing: the goal is to verify the *mechanism* (format iteration →
  `supports_edit()` filter → `supported_extensions()` collection →
  validation/error), not which formats happen to be registered. Write a
  unit test that constructs a `ProjectConfig` with `formats=[SDocFormat()]`
  only (overriding the default list) and asserts
  `get_editable_document_extensions() == [".sdoc"]`, plus a test that adds
  `HTML2PDFFormat()` (`supports_edit() == False`,
  `supported_extensions() == [".pdf"]`) to the list and asserts `.pdf` is
  *not* included in the result. `HTML2PDFFormat` is used instead of a
  fake/stub `Format` because it is a real, permanently non-editable format
  (PDF export is not and will not become UI-editable) with a trivial
  no-arg constructor — add a short comment in the test explaining this
  choice and why a stub was not used. Follow the existing conventions in
  `tests/unit/strictdoc/core/test_project_config.py` (numbered
  `test_NN_description` functions, direct `ProjectConfig(...)`
  instantiation, no mocking framework).

## Known limitation (out of scope for this task)

`write_document_to_file()`
(`strictdoc/server/routers/main_router.py:299-325`) picks the writer by
hardcoding `document.meta.input_doc_full_path.lower().endswith((".md",
".markdown"))`, falling back to the SDoc writer otherwise. It is not
derived from `project_config.formats`/`Format.supports_edit()` at all
(there is already a `FIXME: Factorize this into an OOP class` comment on
it). Once this task makes document-path validation dynamically accept any
editable format's extensions, a project that adds a third editable format
in the future would pass validation but still get silently mis-written by
this hardcoded fallback. Not fixing this now — it would turn a validation
fix into a writer-dispatch refactor — but flagging it as a follow-up
since `Format` has no "write an edited document back to disk" method yet
(`write_converted_document` is for `convert`, not this save path).
