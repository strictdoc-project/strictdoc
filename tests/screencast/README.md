# Screencast scenarios

This directory holds the StrictDoc demo-video pipeline: scenarios that
exercise real StrictDoc UI flows with Playwright, written in Python.

Each scenario is an ordinary pytest test case, and it is dual-purpose:

- run as a normal test, it verifies that the scenario still reflects real
  UI behavior;
- run with `--record-video` (see below), the same test also captures and
  saves a `.webm` video of the scenario.

A failing scenario means its video can no longer be trusted: investigate
before re-recording — it may be a product bug, or an intentional UI change
the scenario doesn't reflect yet. Re-record once the scenario is fixed or
updated and passing again.

## Directory layout

```text
tests/screencast/
├── fixture.py                    # shared fixture-project and port constants
├── fixtures/
│   └── strictdoc-demo-project/   # small, self-contained StrictDoc project used by scenarios
├── helpers/                      # Playwright Page Object helpers (Screen, ViewTypeSelector, ...)
├── scenarios/
│   ├── conftest.py                # `page` fixture (headless Chromium) + --strictdoc-record-video option
│   ├── typing.py                  # fake-typing effect for the IDE-style scene
│   ├── strictdoc_ui/test_case.py
│   └── ide_typing_to_table/test_case.py
├── demo.html                     # standalone HTML playground for IDE/terminal-style scenes
├── run_server.py                 # manual dev server for inspecting a scene in the browser
└── output/                       # generated .webm videos (gitignored)
```

`tests/screencast/helpers/` contains Playwright Page Object helpers
(`Screen`, `ViewTypeSelector`, ...). New scenarios should use and extend
these rather than inlining locators.

## Setup

Playwright's Python package is installed as part of the project's `check`
dependencies (`requirements.check.txt`). The Chromium browser binary is a
separate, one-time step:

```bash
playwright install chromium
```

(Only Chromium is needed — scenarios don't use other browsers.)

## Running the scenarios

```bash
invoke test-screencast
```

This runs every scenario in `tests/screencast/scenarios/` as a fast
pass/fail check, with no video output.

Useful options:

| Option | Purpose |
| --- | --- |
| `--focus=<expr>` | Run only scenarios matching a pytest `-k` expression. |
| `--record-video` | Also (re)generate each scenario's `.webm` into `tests/screencast/output/`, named after the scenario's directory (e.g. `strictdoc_ui.webm`). |

Example:

```bash
invoke test-screencast --record-video
```

## Running the demo server manually

For inspecting a scene in the browser during development:

```bash
invoke screencast-server
```

This starts StrictDoc with the demo fixture project at
`http://127.0.0.1:5111` and keeps running until stopped with Ctrl+C.

If the port is already taken by a previous run of this same demo server, it
is stopped automatically. If it's taken by anything else, the command
refuses to touch it and prints the occupying process(es) along with a
`kill` command to stop them yourself.

Scenario test runs use a separate port (`5112`, see `fixture.py`) so a
manual dev server can stay open while scenarios are (re)recorded.

## Adding a new scenario

1. Add fixture content under `fixtures/strictdoc-demo-project/`, if needed.
2. Create `tests/screencast/scenarios/<scenario_name>/test_case.py` with a
   `Test.test(self, page)` method, using the `helpers/` Page Objects (add
   new ones there if the scenario needs UI areas not covered yet).
3. Run `invoke test-screencast --record-video --focus=<scenario_name>` to
   verify the recording.

Standalone HTML/IDE-style scenes (fake typing effect, terminal look) use
`demo.html` as a local playground: characters are appended directly to a
page element's text content to *look* like typing. This is a visual effect
only — it does not simulate keyboard input and does not type into a real
input, textarea, or code editor.
