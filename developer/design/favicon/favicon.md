# Favicon

StrictDoc's browser-tab favicon is rendered from one Jinja template and
varies by which kind of process is serving it: a local dev server
(`invoke server`, `--debug`), a plain `strictdoc server` run, an
end2end/screencast test server (`SDocTestServer`), or a static docs
export. It also adapts to the browser/OS light/dark color scheme.

## How it works

- Template: `strictdoc/export/html/templates/_shared/favicon.svg.jinja`.
  Takes one parameter, `variant` (`"default"`, `"dev"`, `"test"`, ...).
- Each `variant` defines its own `light_color`/`dark_color` pair, used by
  `@media (prefers-color-scheme: light/dark)` — light/dark adaptation is
  per variant, not shared across all of them. A neutral grey (`#808080`)
  is the fallback for browsers that support neither media query.
- A variant isn't limited to color: the template has an `extra_element`
  extension point (currently unused) for adding markup of its own.
- The root `<svg>` carries `data-testid="{{ variant }}-favicon"`. This
  has no effect on any browser (a favicon is never inserted into a
  page's DOM) — it's there only so unit tests can assert which variant a
  render produced, without depending on colors.
- `resolve_favicon_variant(project_config)` in
  `strictdoc/export/html/html_generator.py` resolves the variant:
  `is_test_env` → `"test"`, `is_debug_mode` → `"dev"`, else `"default"`.
- `render_favicon_svg(project_config, html_templates)` resolves +
  renders in one call.
- Rendering happens once per process, not per HTTP request:
  `HTMLGenerator.export_assets()` — the function that already copies all
  other static assets into the output `_static/` folder exactly once
  per process (server startup, `strictdoc export`, HTML2PDF export) —
  calls `render_favicon_svg()` right after that copy step and writes the
  result to `_static/favicon.svg`, overwriting the plain file just
  copied there. No new server route or in-memory cache was needed for
  this.
- `base.jinja.html`'s
  `<link rel="shortcut icon" href="{{ view_object.render_static_url('favicon.svg') }}">`
  and the server's asset route are unchanged — both still just serve a
  plain file from disk.
- Test-environment signal: `SDocTestServer._get_strictdoc_command()`
  (`tests/end2end/server.py`) sets `STRICTDOC_ENV=test` on the
  subprocess it launches; `strictdoc/cli/main.py` reads it into
  `SDocRuntimeEnvironment.is_test_env` (`strictdoc/core/environment.py`),
  the same way `--debug` is read into `is_debug_mode`.
- Tests: `tests/unit/strictdoc/export/html/test_favicon.py`.
- The original static SVG is kept only as a design source at
  `developer/design/favicon/logo_s.svg` and is never served directly.

## Generating `favicon.ico`

The desktop launcher window icon
(`strictdoc/features/launcher/launcher_frame.py`) uses a separate,
pre-built `strictdoc/export/html/_static/favicon.ico` file — it is not
generated automatically. To regenerate it from `logo_s.svg` (or a
rendered instance of `favicon.svg.jinja`), use one of the two methods
below. Both run entirely locally — no third-party web converters needed.

### Method 1 — single-resolution (quick, no extra installs)

Requires `rsvg-convert` (librsvg) and, on macOS, the built-in `sips`.

```bash
brew install librsvg  # if rsvg-convert isn't already installed

rsvg-convert -w 256 -h 256 \
  developer/design/favicon/logo_s.svg \
  -o favicon_256.png

sips -s format ico favicon_256.png --out favicon.ico
```

Produces a single 256x256 layer; browsers/OS scale it down as needed,
which is normally good enough.

### Method 2 — multi-resolution (16/32/48/256 in one file)

Recommended for the launcher icon, where multi-size looks sharper at
small sizes. Requires `rsvg-convert` plus the `Pillow` Python package
(`pip install Pillow` — a one-off conversion aid, not a project
dependency):

```bash
rsvg-convert -w 256 -h 256 \
  developer/design/favicon/logo_s.svg \
  -o favicon_256.png

python3 - <<'EOF'
from PIL import Image

img = Image.open("favicon_256.png")
img.save(
    "favicon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48), (256, 256)],
)
EOF
```

`Image.save(..., sizes=[...])` resamples the source PNG down to each
requested size and bundles all of them into one `.ico`.

To convert a *rendered* favicon (a specific variant) instead of the
plain source SVG, render `favicon.svg.jinja` to a `.svg` file first,
then feed that file to either method above instead of `logo_s.svg`.
