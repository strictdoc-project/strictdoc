# Favicon variants for StrictDoc's own execution contexts

## WHAT

- StrictDoc's browser-tab favicon distinguishes, at a glance, which kind of
  StrictDoc instance a tab belongs to, within our own development
  ecosystem:
  - a local developer server (`invoke server`, i.e. `--development` mode),
  - a StrictDoc server as deployed/run by an end user (`strictdoc server`,
    no `--development`),
  - a test server (end2end/screencast scenarios, `SDocTestServer`),
  - the published static documentation site (GitHub Pages export).
- The favicon additionally adapts to the browser/OS light/dark color
  scheme where the browser supports it (`prefers-color-scheme`), and this
  adaptation is defined independently for each instance kind above — not
  just for a single default look.
- There continues to be exactly one favicon source to maintain (a single
  Jinja template; no set of hand-duplicated SVG files to keep in sync when
  the logo changes). The original static SVG is kept only as a design
  reference under `developer/design/favicon/logo_s.svg` and is never
  served directly.
- Out of scope:
  - End-user-facing icon customization/branding for a project's own
    `"default"`-variant favicon — tracked separately in
    `developer/tasks/20260708_favicon_vars/task_custom_favicon.md`.
  - The desktop launcher window icon (`favicon.ico`, used by
    `strictdoc/features/launcher/launcher_frame.py`) — a separate asset,
    not the browser-tab favicon. How to regenerate it from the design
    source, if ever needed, is documented separately in
    `developer/design/favicon/favicon.md`.
  - `prefers-contrast`, `forced-colors`, `prefers-reduced-motion` handling
    — worth a future follow-up, not required here.

## WHY

- Today, `base.jinja.html` links a single static asset via
  `view_object.render_static_url()`, and every execution context — dev
  server, a user's deployed server, test servers, the exported docs site —
  renders the exact same icon.
- When developing StrictDoc itself, it's common to have several of these
  running side by side (a dev server, a manually-started screencast/e2e
  test server, a plain `strictdoc server` for comparison). With identical
  favicons, telling their browser tabs/windows apart requires reading the
  tab title or URL every time.
- This is purely an internal developer-ergonomics improvement to our own
  ecosystem, not a product feature for StrictDoc's end users.

## HOW

- **Two independent signals, two different mechanisms.** These must not be
  conflated:
  - *Light/dark scheme* is an ambient, client-side signal
    (`prefers-color-scheme`), evaluated by the browser against whatever
    SVG document it loads as the favicon — the server has no say in it.
  - *Which kind of instance this is* (dev / user-deployed / test / docs
    export) is server-side state. There is no CSS/browser feature that can
    express this — it has to be baked into the bytes of the SVG that a
    given process actually serves.

- **The favicon is a single Jinja template, not a static file.**
  `strictdoc/export/html/templates/_shared/favicon.svg.jinja` is
  parameterized by one string, `variant` (e.g. `"default"`, `"dev"`,
  `"test"`), that identifies the instance kind:
  - Each `variant` defines its own `light_color`/`dark_color` pair used by
    the `@media (prefers-color-scheme: light/dark)` rules, so the
    light/dark adaptation is defined per variant rather than shared by
    all of them.
  - A neutral grey (`#808080`) fill/stroke is the fallback for browsers
    that evaluate neither media query (no `prefers-color-scheme` support,
    no resolvable preference).
  - A variant is not limited to color: the template has an
    `extra_element` extension point (currently unused by any variant) for
    adding markup of its own, if a color pair alone isn't enough to
    distinguish it.
  - The root `<svg>` carries `data-testid="{{ variant }}-favicon"`. This
    has no effect on any browser — a favicon is never inserted into a
    page's DOM — it exists purely so unit tests can assert which variant
    a given render produced, without depending on colors that are
    expected to change over time. See
    `tests/unit/strictdoc/export/html/test_favicon.py`.

- **Where `variant` comes from — three signals:**
  - A hidden (not shown in `--help`) CLI flag, `--development`
    (`strictdoc/cli/cli_arg_parser.py`), read into
    `SDocRuntimeEnvironment.is_development_mode`
    (`strictdoc/cli/main.py`, `strictdoc/core/environment.py`).
    `invoke server`'s dev task (`tasks.py`) passes `--development`
    alongside `--debug` (which controls verbose error/stack-trace output
    and is unrelated to `variant` resolution).
    `project_config.environment.is_development_mode` resolves to
    `variant="dev"`.
  - A flag for test servers: `SDocTestServer._get_strictdoc_command()`
    (`tests/end2end/server.py`) sets `STRICTDOC_ENV=test` on the
    subprocess it launches; `strictdoc/cli/main.py` reads it into
    `SDocRuntimeEnvironment.is_test_env`, exposed the same way
    `is_development_mode` is. This resolves to `variant="test"`.
  - `ProjectConfig.is_running_on_server` (existing, set by the live
    server's router setup) distinguishes a live server from a static
    export: when `False`, resolves to `variant="export"` (`strictdoc
    export`, HTML2PDF export).
  - A user's plain `strictdoc server` run is what's left once
    `is_test_env`, `is_development_mode` are both false and
    `is_running_on_server` is true: `variant="default"`.
  - `resolve_favicon_variant(environment, is_running_on_server) -> str`
    (`strictdoc/core/project_config.py`) implements this resolution once,
    in one place; `ProjectConfig.get_favicon_variant()` calls it with
    `self.environment` and `self.is_running_on_server`.

- **Rendering happens once per process/run, not per request.** None of
  the flags that decide `variant` change during a process's lifetime, so:
  - `render_favicon_svg(project_config, html_templates) -> str` resolves
    the variant and renders the template in one call.
  - `HTMLGenerator.export_assets()` — the function that already
    `sync_dir`-copies every other static asset into the output `_static/`
    folder exactly once per process (once at server startup, once during
    `strictdoc export`/HTML2PDF export) — calls `render_favicon_svg()`
    right after that copy step and writes the result to
    `_static/<ProjectConfig.get_favicon_filename()>` (`favicon.svg` for
    this task; see `task_custom_favicon.md` for the other case).
  - This single code path serves both the live server
    (`strictdoc/server/routers/main_router.py`) and static export
    (`strictdoc/features/html2pdf/html2pdf_generator.py`,
    `strictdoc export`). No new server route or in-memory cache is
    needed: the existing "render/copy once into the output tree"
    pipeline already gives "rendered once per process" for free.
  - `base.jinja.html`'s `<link rel="shortcut icon">` reads its `href`
    and `type` from `ProjectConfig.get_favicon_filename()`/
    `get_favicon_mime_type()`; the server's asset route is unchanged and
    still just serves a plain file from disk.

- **Verification.** `tests/unit/strictdoc/export/html/test_favicon.py`
  covers: `ProjectConfig.get_favicon_variant()` for each flag combination;
  that the template tags its output with the expected `data-testid` for
  each variant; and that `render_favicon_svg()` correctly threads the
  resolved variant into the template through a real `HTMLTemplates`
  instance (guarding the Python → Jinja handoff, not just each half in
  isolation). Manually cross-check the visual result for the
  dev server, a plain `strictdoc server`, and a screencast/e2e test server
  (e.g. via `invoke screencast-server`) side by side in a browser that
  supports `prefers-color-scheme` for favicons (Chromium/Edge) and one
  that doesn't (Firefox), confirming each variant's light/dark colors
  render as expected in both.

- **Explicitly not doing:** per-project favicon theming for end users
  (tracked separately, see `task_custom_favicon.md`), animating the
  favicon, handling `forced-colors`/`prefers-contrast`, or a fixed badge
  shape/icon — distinguishing variants is expressed purely through their
  own `light_color`/`dark_color` (and, if ever needed, the
  `extra_element` extension point), not a hardcoded decoration.
