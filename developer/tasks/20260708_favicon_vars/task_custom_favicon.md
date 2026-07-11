# Custom favicon for a project's own StrictDoc instance

## WHAT

- Let a project supply its own favicon file, replacing StrictDoc's icon
  for the `"default"` and `"export"` variants — see
  `developer/tasks/20260708_favicon_vars/task.md` for what these variants
  mean (a user-deployed `strictdoc server` run, and a static `strictdoc
  export`/HTML2PDF export, respectively).
- `"dev"` and `"test"` always keep rendering StrictDoc's own favicon
  regardless of whether a custom favicon is configured — a developer must
  always be able to tell a dev/test instance apart, even in a project
  that has one set.
- Out of scope: the desktop launcher window icon (`favicon.ico`); per-tab
  favicon animation.

## WHY

- There is currently no such mechanism, despite an earlier (incorrect)
  claim in `task.md` that one existed. `dir_for_sdoc_assets`
  (`strictdoc/core/project_config.py`) only renames StrictDoc's own
  output asset folder — it does not let a project inject or override any
  asset file.
- Projects/teams branding their generated documentation site want their
  own icon on the browser tab, not StrictDoc's logo.

## HOW

- Add an optional `ProjectConfig` field, `favicon_path: Optional[str]`,
  following the existing `html2pdf_template` pattern: a path relative to
  the project root, validated to exist and resolved to absolute in
  `validate_and_finalize()`.
- Any file format is allowed (`.ico`, `.png`, `.svg`, ...) — not
  SVG-only. `ProjectConfig.get_custom_favicon_path()` returns
  `favicon_path` unless `get_favicon_variant()` resolves to `"dev"` or
  `"test"` (`None` in those two cases).
  `HTMLGenerator.export_assets()`
  (`strictdoc/export/html/html_generator.py`) copies that file to
  `_static/favicon.<their-extension>` instead of rendering
  `favicon.svg.jinja` whenever it's not `None`.
- `base.jinja.html`'s `<link rel="shortcut icon" href="...favicon.svg"
  type="image/svg+xml">` hardcodes both the filename and the SVG mime
  type today; both need to become dynamic:
  `ProjectConfig.get_favicon_filename()`/`get_favicon_mime_type()`
  (MIME type via `mimetypes.guess_type()`, already used the same way in
  `strictdoc/server/routers/main_router.py:4780` for other assets),
  reached from the template the same way `project_config` is already
  reachable from view objects there.
- Verification: a unit test asserting that with `favicon_path` set, the
  `"default"`/`"export"` variants copy the user's file bytes into
  `_static/favicon.<ext>` unchanged and the rendered `<link>` tag points
  at that filename/MIME type, while `"dev"`/`"test"` still render
  `favicon.svg.jinja` at `_static/favicon.svg` regardless.
