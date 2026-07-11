# Manual test: custom favicon for a StrictDoc project

Verifies that a project can replace StrictDoc's browser-tab favicon with
its own file (`ProjectConfig.favicon_path`), and that this only affects
the `"default"` variant (a plain `strictdoc server`/`strictdoc export`),
not `"dev"`/`"test"`.

## 1. Create a fresh test project

```bash
strictdoc new /tmp/sdoc_manual_favicon_demo
```

This generates `strictdoc_config.py`, `docs/`, and `src/` under
`/tmp/sdoc_manual_favicon_demo`.

## 2. Add a custom favicon file

Any SVG works for a visible, obviously-custom check — a plain red circle
is the simplest:

```bash
cat > /tmp/sdoc_manual_favicon_demo/my_favicon.svg <<'EOF'
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="45" fill="red"/>
</svg>
EOF
```

## 3. Point the project config at it

Edit `/tmp/sdoc_manual_favicon_demo/strictdoc_config.py` and add
`favicon_path="my_favicon.svg"` as a `ProjectConfig(...)` argument (path
is relative to the project root):

```python
def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Hello World",
        project_features=[...],
        include_doc_paths=["/docs/"],
        include_source_paths=["/src/**"],
        favicon_path="my_favicon.svg",
    )
```

## 4. Start the server

```bash
strictdoc server --no-reload --port 18400 /tmp/sdoc_manual_favicon_demo
```

(`--no-reload` avoids the file-watcher relaunching mid-test; any free
port works instead of `18400`.)

## 5. Verify from the command line (optional, before opening a browser)

```bash
curl -s http://127.0.0.1:18400/ | grep "shortcut icon"
# expect: <link rel="shortcut icon" href="_static/favicon.svg" type="image/svg+xml" />

curl -s -o /dev/null -w "favicon http status: %{http_code}\n" \
  http://127.0.0.1:18400/_static/favicon.svg
# expect: favicon http status: 200
```

## 6. Open in a browser

Open **http://127.0.0.1:18400/** — the browser tab should show the red
circle instead of StrictDoc's own logo.

Direct file check: http://127.0.0.1:18400/_static/favicon.svg

## 7. (Optional) Confirm dev mode ignores the custom favicon

Start the same project with `--debug` on a different port and confirm
the tab shows StrictDoc's own `dev`-tagged icon instead, even though
`favicon_path` is still configured:

```bash
strictdoc --debug server --no-reload --port 18401 /tmp/sdoc_manual_favicon_demo
curl -s http://127.0.0.1:18401/_static/favicon.svg | grep data-testid
# expect: data-testid="dev-favicon"
```

## 8. Clean up

```bash
# Ctrl-C the server(s) started in steps 4 and 7, then:
rm -rf /tmp/sdoc_manual_favicon_demo
```
