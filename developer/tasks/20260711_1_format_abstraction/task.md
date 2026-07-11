# Introduce Format abstration

## WHY

User needs:

- StrictDoc users need to read and write RST, AsciiDoc, possibly OpenFastTrace Markdown or other Markdown dialects, the SPDX format, and other formats.
- StrictDoc users need to write their own custom import and export converters for formats such as Markdown or Excel. It is very difficult to write a single generator for these and other formats that can automatically detect all nuances of an unlimited number of custom schemas. This drives the idea of a `Format` abstraction and the possibility for users to create their own formats.
- StrictDoc users need write their own custom generators or features for `export`, `import`, or other commands. This second type of feature is related to, but mostly orthogonal to, the `Format` feature. It is kept out of scope for this task and mentioned here only as a future development prospect.

## WHAT

Introduce a new `Format` abstraction which is a Python abstract class.

The new abstraction should be the top-level abstraction for all existing formats:

- HTML (handle `html`)
- SDoc (handle `sdoc`)
- Markdown (handle `markdown`)
- ReqIF (handles `reqif-sdoc` and `reqifz-sdoc` — one `ReqIFFormat` class
  covering both the zipped and non-zipped variants, matching today's
  `ReqIFExport.export(reqifz=bool)` call shape)
- RST (handle `rst`)
- SPDX (handle `spdx`)
- Excel (handle `excel`)
- HTML2PDF (handle `html2pdf`)
- Doxygen (handle `doxygen`)
- JSON (handle `json`)

This is the full set of formats currently listed in `EXPORT_FORMATS`
(`commands/export.py`), now including plain `html` (originally omitted from
this list, but too central/complex to leave un-migrated — it's what
`html2pdf`'s own export code is currently nested inside and shares
`HTMLTemplates` setup with). All 10 must be covered so no existing export
path is left un-migrated.

The DocumentFinder shall be updated to rely on the currently available Formats where each format should be support a boolean method whether this format supports reading files as well as a method that actually converts the input file to an SDoc in-memory object.

## HOW

### The abstract interface

The abstract interface for each Format class shall support these methods:

```py
def supported_extensions() -> list[str]:

def supports_read() -> bool:
def supports_import() -> bool:
def supports_export() -> bool:
def supports_grammar() -> bool:

def read_from_file(
    self, doc_file: File, project_config: ProjectConfig
) -> SDocDocument:

def grammar_extensions() -> list[str]:
def read_grammar(
    self, doc_file: File, project_config: ProjectConfig
) -> DocumentGrammar:

def export_complete_tree() -> None:
def export_single_document() -> None:
def import_file(...) ...
def import_folder(...) ...
```

Note: `read_from_file()`/`read_grammar()` take the `File` object
(`strictdoc.core.file_system.file_tree.File`), not a bare path string, even
though the WHAT section above says "an SDoc in-memory object" from "the
input file" without specifying the exact parameter type. This was decided
during implementation: `JUnitXMLReader`/`GCovJSONReader`/
`RobotOutputXMLReader.read_from_file()` all require the `File` object (they
need `level`/`rel_path`, which can't be safely reconstructed from a bare
path string outside of `DocumentFinder`'s own tree-walk). Since
`DocumentFinder` already has the `File` object at the call site, and
`doc_file.full_path` trivially gives the plain string the other readers
need, taking `File` uniformly is the behavior-preserving choice.

Only `SDocFormat` and `MarkdownFormat` implement `supports_grammar()` /
`grammar_extensions()` / `read_grammar()`; every other Format class returns
`False`/empty and doesn't override `read_grammar()`. Only `SDocFormat`,
`MarkdownFormat`, `ReqIFFormat`, `JUnitXMLFormat`, `GCovJSONFormat`,
and `RobotXMLFormat` implement `supports_read()`/`read_from_file()`.

Note:
`strictdoc/backend/sdoc_source_code/test_reports/junit_xml_reader.py` used
to define an unrelated `JUnitXMLFormat(IntEnum)` (JUnit dialect detection:
LLVM_LIT/CTEST/GOOGLE_TEST/PYTEST/CARGO_NEXTEST). That enum was renamed to
`JUnitXMLDialect` so the new read-only Format class could take the
`JUnitXMLFormat` name.

### Reading formats (native DocumentFinder dispatch)

`DocumentFinder` (`strictdoc/core/file_system/document_finder.py`) already
cleanly separates file discovery (`_build_file_tree`, a hardcoded extension
list) from parsing (`_process_worker_parse_document`, an if/elif dispatch by
extension to a reader class). This is the seam this task plugs into: the
discovery extension list and the parsing dispatch should both be derived
from the registered Formats instead of hardcoded.

Today's dispatch covers two genuinely different return types:

- **Documents** (`-> SDocDocument`): `.sdoc` (`SDReader`), `.md`/`.markdown`
  (`SDMarkdownReader`), `.reqif` (`ReqIFReader` — a *native* reader, distinct
  from the one-shot `import reqif` command's `ReqIFImport`), `.junit.xml`
  (`JUnitXMLReader`), `.gcov.json` (`GCovJSONReader`), `.robot.xml`
  (`RobotOutputXMLReader`).
- **Grammars** (`-> DocumentGrammar`): `.gra.md` (`MarkdownGrammarReader`),
  `.sgra` (`SDocGrammarReader`).

Decisions:

- **Documents**: add `supports_read() -> bool` and
  `read_from_file(self, file_path: str, project_config: ProjectConfig) ->
  SDocDocument` to the `Format` interface (default: not supported, like
  `supports_import()`).
  - `SDocFormat.read_from_file()` wraps `SDReader`.
  - `MarkdownFormat.read_from_file()` wraps `SDMarkdownReader`.
  - `ReqIFFormat.read_from_file()` wraps the native `ReqIFReader` — this is
    a *second*, separate underlying reader from `ReqIFFormat.import_file()`
    (which wraps `ReqIFImport`, the one-shot `import reqif` CLI command).
    Both stay on `ReqIFFormat`, matching the fact that these are already two
    distinct code paths today.
  - Three new read-only Format classes are needed, since none exist yet:
    `JUnitXMLFormat`, `GCovJSONFormat`, `RobotXMLFormat`. These wrap
    `JUnitXMLReader`/`GCovJSONReader`/`RobotOutputXMLReader` respectively.
    `supports_read() == True`; `supports_export()` and `supports_import()`
    are `False` — there is no CLI `--formats`/`import` counterpart for
    these, only native `DocumentFinder` discovery. They therefore don't
    need a CLI-facing `handles()` entry (nothing ever requests them via
    `--formats`), but still need `supported_extensions()` for discovery
    (`.junit.xml`, `.gcov.json`, `.robot.xml` respectively).
- **Grammars**: rather than a separate `GrammarFormat` class, extend the
  *same* per-syntax Format class with `supports_grammar() -> bool`,
  `grammar_extensions() -> List[str]`, and
  `read_grammar(self, file_path: str, project_config: ProjectConfig) ->
  DocumentGrammar`. Grammar-reading for a syntax belongs on the same class
  that already owns document-reading for that syntax (markdown-syntax
  grammar and markdown-syntax documents are "the same format," just applied
  to a different kind of file) — a separate `GrammarFormat` would fragment
  that instead of centralizing it.
  - `SDocFormat.read_grammar()` wraps `SDocGrammarReader` (`.sgra`).
  - `MarkdownFormat.read_grammar()` wraps `MarkdownGrammarReader`
    (`.gra.md`).
  - All other Format classes: `supports_grammar() == False`.

`strictdoc/server/document_watcher.py` independently hardcodes the same
extension list (`WATCHED_DOCUMENT_EXTENSIONS`) for filesystem-watch/rebuild
triggering. This task should update it to derive its list from the same
Format-driven source (discovery extensions ∪ grammar extensions for formats
with `supports_read()`/`supports_grammar()`), so it can no longer drift out
of sync with `DocumentFinder`.

#### Implementation status: done

All of the above is implemented. Two deviations from this section's exact
wording, both discovered during implementation and necessary to preserve
current behavior exactly:

- `read_from_file()`/`read_grammar()` take the `File` object
  (`strictdoc.core.file_system.file_tree.File`), not a bare path string —
  see the note under "The abstract interface" above.
- A separate `read_extensions() -> List[str]` method was added (default
  `[]`), distinct from `supported_extensions()`. This exists because
  `ReqIFFormat.supported_extensions()` lists both `.reqif` and `.reqifz`
  (used for export-file naming), but `DocumentFinder` today only
  auto-discovers/reads `.reqif` natively, never `.reqifz`. Reusing
  `supported_extensions()` for discovery would have silently started
  auto-discovering `.reqifz` files too — a behavior change. Only
  `SDocFormat` (`.sdoc`), `MarkdownFormat` (`.md`, `.markdown`),
  `ReqIFFormat` (`.reqif` only), `JUnitXMLFormat` (`.junit.xml`),
  `GCovJSONFormat` (`.gcov.json`), and `RobotXMLFormat` (`.robot.xml`)
  override it.

`DocumentFinder._build_file_tree()`/`_process_worker_parse_document()` now
build a single dispatch table from `project_config.formats`
(`strictdoc/core/file_system/document_finder.py:_build_extension_dispatch_table`),
sorted longest-extension-first (so `.gra.md` is matched before `.md`, the
one real suffix-overlap case) instead of a hardcoded if/elif chain.
`document_watcher.py` derives `watched_extensions` from the same source via
`get_watched_document_extensions()`, passed in from `main_router.py`; its
module-level `WATCHED_DOCUMENT_EXTENSIONS` tuple remains only as the default
for callers (e.g. unit tests) that construct `DocumentWatcher` directly
without a `ProjectConfig`.

Verified: all 619 unit tests pass; ruff/ruff-format/mypy all clean;
integration tests for markdown (including `.gra.md` grammar-from-file/alias
cases), sdoc, reqif (including native `read_reqif`), JUnit XML (lit/ctest/
gtest/pytest/cargo-nextest dialects), GCov JSON, Robot XML, and
source-code-traceability (102 tests) all pass unchanged.

**HTML2PDF** is a genuine `Format`: it produces PDF output (via the HTML
templates as an intermediate step), export-only, `supports_import() ==
False`. It stays in the `Format` list, not a future `Feature`.

**Doxygen** is the weaker fit: it builds a derived cross-reference artifact
rather than representing the document tree as an interchange format, and is
a likely candidate to move to a future `Feature` abstraction (see WHY).
Treat it as `Format`-shaped for this task (export-only, like HTML2PDF), but
don't be surprised if it gets reclassified later.

Example of a format class: `MarkdownFormat`.

The code from `ExportAction` should be properly allocated to each Format class. The `ExportAction` should only iterate over the registered format classes and only call them if the `self.project_config.export_formats` actually requests them.

This is a pure refactor: behavior must be fully preserved. Most formats
already have a de facto exporter class today (`HTMLGenerator`,
`HTML2PDFGenerator`, `DocumentRSTGenerator`, `ExcelGenerator`, `ReqIFExport`,
`SPDXGenerator`, `JSONGenerator`, `DoxygenGenerator`); only `sdoc` and
`markdown` export are currently inline methods on `ExportAction`
(`export_sdoc`, `export_markdown`) and need to be extracted into their own
Format classes.

### Custom formats via project config

Users should be able to register their own `Format` subclasses via the
Python project config, e.g.:

```py
formats=[*ProjectConfig.default_formats(), CustomMarkdownOftFormat()]
```

- Add a `formats` field to `ProjectConfig`, defaulting to
  `ProjectConfig.default_formats()` (the 9 built-in Format instances).
- `ExportAction` iterates `self.project_config.formats` instead of the
  current hardcoded `if fmt in self.project_config.export_formats` chain.
  This falls out naturally from the Format abstraction itself and requires
  no extra mechanism beyond it.

### CLI support for custom format handles (e.g. `--formats markdown_oft`)

This is the tricky part: today `_check_formats()`
(`strictdoc/commands/export.py:27-35`) validates `--formats` against the
static `EXPORT_FORMATS` list *during argparse parsing*, which happens before
`ProjectConfigLoader.load_using_export_config()` loads the project config
(`ExportCommand.run`, `strictdoc/commands/export.py:195`) — i.e. before any
custom Format registered in that config is known.

Proposed approach: a two-pass parse in the `export` command.

1. First pass: extract only `--config` (and no other argument) from
   `sys.argv` to locate the project config file.
2. Load the project config (or at least its `formats` list) to obtain the
   registered custom Format handles.
3. Extend the allowed choices for `--formats` with those custom handles,
   then perform the real argparse parse/validation.

This keeps the change contained to `strictdoc/commands/export.py`; the
static `EXPORT_FORMATS` constant becomes derived (built-ins plus whatever
custom formats the config declares) rather than a fixed list. It relies on
project-config loading not itself depending on the final `--formats` value,
which is true today.

`strictdoc/features/launcher/launcher_frame.py:117` currently imports
`EXPORT_FORMATS` directly to populate its own UI list of export formats.
Once `EXPORT_FORMATS` becomes derived from the registered Format classes
(built-ins plus any custom ones from the loaded project config), the
launcher must pick up that same derived list so custom formats also appear
as options in the launcher UI, not just on the CLI.

### Scope clarifications

- **`export_single_document()`**: today only HTML actually supports a
  single-document export path (`HTMLGenerator.export_single_document`); every
  other format only supports whole-tree export. For formats that don't
  support single-document export today (RST, Excel, ReqIF, SPDX, JSON,
  Doxygen, SDoc, Markdown), `export_single_document()` must raise
  `NotImplementedError` (or equivalent) rather than gain new functionality.
  Building real single-document export for these formats is explicitly out
  of scope for this task.
- **`import_file()` / `import_folder()`**: today only ReqIF and Excel have a
  real "import" path (via `ImportAction`, separate from `ExportAction`).
  Only `ReqIFFormat` and `ExcelFormat` should implement real import; all
  other Format classes report `supports_import() == False` and their
  `import_file()`/`import_folder()` are not implemented. Markdown's native
  reader (`SDMarkdownReader`, wired directly into
  `TraceabilityIndexBuilder`) is a first-class parser, not a conversion-style
  import, and stays outside this abstraction — it is explicitly out of
  scope.
