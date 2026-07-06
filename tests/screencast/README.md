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
`http://127.0.0.1:5301` and keeps running until stopped with Ctrl+C.

If the port is already taken by a previous run of this same demo server, it
is stopped automatically. If it's taken by anything else, the command
refuses to touch it and prints the occupying process(es) along with a
`kill` command to stop them yourself.

Scenario test runs use a separate port (`5302`, see `fixture.py`) so a
manual dev server can stay open while scenarios are (re)recorded.

### Previewing a scenario that doesn't use the shared fixture

Some scenarios (e.g. `hello_world`) don't browse the shared fixture
project — they generate their own project from scratch (via a real
`strictdoc new` call) inside the test itself, in a pytest `tmp_path` that's
deleted right after the test finishes. There's nothing left on disk
afterwards to point a manual server at.

To preview one of these, pass `--focus=<scenario_name>`:

```bash
invoke screencast-server --focus=hello_world
```

This looks up the scenario in `tests/screencast/manual_scenarios.py`,
which knows how to (re)create that scenario's project on demand, and
serves it on the same port/URL as the default case
(`http://127.0.0.1:5301`).

The generated project is written to
`build/screencast_manual/<scenario_name>/` — a disposable, gitignored
build artifact (see `/build/` in `.gitignore`), **not** a fixture. It's
left in place between runs (instead of being regenerated every time) so
that:

- restarting the manual server doesn't rerun the scenario's setup (e.g.
  `strictdoc new`) and doesn't hit its refusal to overwrite existing
  files;
- any manual edits made through the UI while inspecting the scene survive
  a server restart.

Delete `build/screencast_manual/` (or the specific scenario's
subdirectory) at any time to reset it back to a clean, freshly generated
state on the next run.

Adding a new scenario that needs this kind of on-demand project also means
adding an entry for it to the `SCENARIOS` registry in
`tests/screencast/manual_scenarios.py`.

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
