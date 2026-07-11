# Replace CLI "import" command with a "convert" command

## WHY

Since SDoc is not the only base format that StrictDoc works with (Markdown is
another default now).

## WHAT

StrictDoc shall implement the `convert` command instead of `import` which
accepts the `--input-format` (default: auto-discover from extension) and
`--output-format` (default: SDoc) arguments.

The editable interface's behavior for Import from ReqIF shall not be affected
in terms of observable behavior.

## HOW

- `convert` replaces `import`. `import` goes away.
- Migrate all existing Excel and ReqIF tests from using `import` to `convert`.
- `convert` is a single flat command (like `export`), not a subcommand
  family: `strictdoc convert <input_path> <output_path> --input-format=... --output-format=...`.
  Format-specific arguments that today live on the per-format `import`
  subcommands (Excel's `parser` positional; ReqIF's `profile` positional,
  `--reqif-enable-mid`, `--reqif-import-markup`) become optional flags on the
  single `convert` command instead (e.g. `--excel-parser`, `--reqif-profile`,
  `--reqif-enable-mid`, `--reqif-import-markup`), mirroring how `export`
  already carries format-specific flags (`--reqif-profile`, etc.) alongside
  generic ones.
- `--output-format` defaults to `sdoc` and, for this task, `sdoc` is the only
  implemented/valid choice — the flag exists for future-proofing (per the
  WHY: Markdown is also a base format now), but writing a converted document
  out as Markdown or any other format is explicitly out of scope here.
- `--input-format`/`--output-format` choices are Format-driven, not
  hardcoded: discovered dynamically from the registered `Format` classes
  (`supports_import()`/similar), the same two-stage `--config` preparse
  pattern already used for `export --formats` and the `import` subcommand
  family (see `developer/tasks/20260711_2_connect_import_to_formats/`).
- `--input-format` defaults to auto-discovery from the `input_path`
  extension, using each Format's `supported_extensions()`/
  `read_extensions()`.
- `--input-format` values reuse `Format.handles()` (the same vocabulary as
  `export --formats`), not a separate import-only name: for ReqIF this means
  `reqif-sdoc` / `reqifz-sdoc` (matching `.reqif` / `.reqifz` respectively)
  rather than a single `reqif` value, even though both handles behave
  identically on the import side and the extension already discloses which
  one it is.
