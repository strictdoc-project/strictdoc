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

## Quick reference

Commands:

| Command | Effect |
| --- | --- |
| `invoke test-screencast` | Run every scenario, fast pass/fail, no video. |
| `invoke test-screencast --focus=<expr>` | Run only scenarios matching a pytest `-k` expression. |
| `invoke test-screencast --record-video` | Also (re)generate every scenario's `.webm`. |
| `invoke test-screencast --record-video --focus=<name>` | (Re)generate just one scenario's `.webm`. |
| `invoke screencast-server` (alias `scs`) | Manual server on a disposable copy of the shared fixture, at `http://127.0.0.1:5301`. |
| `invoke screencast-server --focus=<scenario>` | Manual server on a disposable copy of a specific scenario's project instead. |
| `invoke screencast-server --edit [--focus=<scenario>]` | Same, but on the real, persistent files — changes through the UI stick around. |
| `playwright install chromium` | One-time setup — see "Setup" below. |

Where to change what:

| To change... | Edit... |
| --- | --- |
| Video/viewport resolution | `VIEWPORT_SIZE` in `scenarios/conftest.py`. |
| Pauses between steps | `pause()` calls in a scenario (`helpers/pacing.py`). |
| Pause before a click, or typing speed | `pause_ms`/`delay_ms` args on `Pointer.click`/`move_to`/`type_into` calls. |
| Cursor/highlight look (color, size, shape) | `helpers/pointer.css`. |
| Terminal/editor/IDE scene visuals (layout, colors) | `terminal.html` / `editor.html` / `demo.html` (plain CSS). |
| What a scene shows, or when | The scenario's `test_case.py`, or `helpers/editor_scene.py`. |
| `.sdoc` syntax colors in the editor scene | Not here — it reuses the product's own `strictdoc/export/html/_static/pygments.css`. |
| Which project a manual server (`--focus=`) serves | `manual_scenarios.py`'s `SCENARIOS` registry. |

Each row is explained in its own section below.

## Directory layout

```text
tests/screencast/
├── fixture.py                    # shared fixture-project and port constants
├── fixtures/
│   └── strictdoc-demo-project/   # small, self-contained StrictDoc project used by scenarios
├── manual_scenarios.py           # registry used by `invoke screencast-server --focus=...`
├── helpers/                      # Playwright Page Object helpers, see below
├── scenarios/
│   ├── conftest.py                # `page` fixture (headless Chromium, VIEWPORT_SIZE) + --strictdoc-record-video option
│   ├── typing.py                  # fake-typing effect for the IDE-style scene
│   ├── strictdoc_ui/test_case.py
│   ├── ide_typing_to_table/test_case.py
│   └── hello_world/test_case.py   # strictdoc new -> web UI -> editor reveal, see below
├── demo.html                     # standalone HTML playground for the IDE-style scene
├── terminal.html                 # standalone HTML playground: full-frame terminal look
├── editor.html                   # standalone HTML playground: code-editor look (tab + line numbers)
├── run_server.py                 # manual dev server for inspecting a scene in the browser
└── output/                       # generated .webm videos (gitignored)
```

`tests/screencast/helpers/` contains Playwright Page Object helpers. New
scenarios should use and extend these rather than inlining locators or
raw `page.click()`/`page.fill()` calls:

| Helper | Covers |
| --- | --- |
| `screen.py` (`Screen`) | Generic viewtype/header assertions. |
| `viewtype_selector.py` | Switching between document viewtypes (table, ...). |
| `project_tree.py` (`ProjectTree`) | Project index: document list, "add document" modal. |
| `actions_menu.py` (`ActionsMenu`) | The header's `...` actions menu. |
| `form.py` / `form_add_document.py` / `form_edit_requirement.py` | Filling in and submitting `sdoc-form` modals. |
| `node.py` (`Node`, `DocumentRoot`, `Requirement`, `AddNode_Menu`) | Opening a node's menu and adding a child/sibling node. |
| `pointer.py` (`Pointer`) | Makes clicks/typing visible on camera — see below. |
| `pacing.py` (`pause`) | Deliberate beats between steps — see below. |
| `editor_scene.py` | Drives the `editor.html` code-reveal scene — see below. |

## Video resolution

Both the browser viewport and the recorded `.webm`'s resolution come from
a single constant, `VIEWPORT_SIZE` in `scenarios/conftest.py`. Change it
there to change every scenario's output size; there's no per-scenario
override.

## Pacing: controlling pauses

Screencasts need deliberate pauses that a functional test wouldn't
(there's no viewer to wait for otherwise). There are a few independent
knobs:

| What | Where | Default |
| --- | --- | --- |
| A beat between steps/scenes | `pause(page, seconds=...)` from `helpers/pacing.py`, called explicitly in a scenario | 1.0s |
| Pause after the cursor arrives, before clicking | `Pointer.click(target, pause_ms=...)` | 400ms |
| Pause after moving to a target (`Pointer.move_to`) | `Pointer.move_to(target, pause_ms=...)` | 300ms |
| Typing speed in form fields | `Pointer.type_into(target, text, delay_ms=...)` | 35ms/char |
| Typing speed in `demo.html`/`terminal.html` scenes | `type_text(locator, text, delay_ms=...)` in `scenarios/typing.py` | 45ms/char |
| Line-reveal speed in the editor scene | `editor_scene.reveal_added_lines(page, text, line_delay_ms=...)` | 350ms/line |

None of this belongs in a real (future) Playwright e2e suite — there,
actions should run at Playwright's normal speed with its built-in
actionability waits, not with artificial pauses. `Pointer`/`pause()` are
screencast-only, for the benefit of a human watching the video.

## Making clicks visible: the fake cursor and highlight

Playwright doesn't render a real OS mouse cursor, so a driven click is
otherwise invisible in a recording. `helpers/pointer.py`'s `Pointer`
injects:

- a small dot that follows real `mousemove` events (dispatched by
  `page.mouse.move(..., steps=N)`, so it visibly travels rather than
  teleporting), and
- a pulsing outline that highlights the click target just before the
  click.

This is registered via `page.add_init_script()`, so it re-applies
automatically on every navigation within a scenario (a `file://` scene,
the live server, another `file://` scene, ...) — no need to re-inject it
per page.

To change how the cursor or highlight *look* (color, size, shape,
animation), edit `helpers/pointer.css` — plain CSS, no build step. Its
content is read and spliced into the injected script at import time (via
`json.dumps()`, so any CSS content is safe to use there, including quotes
or backslashes).

## Editing scene visuals (terminal, editor, IDE)

`demo.html`, `terminal.html`, and `editor.html` are self-contained HTML
files with an inline `<style>` block each — no bundler, no CSS framework.
Open one directly and edit its `<style>`:

- `terminal.html`: a full-frame dark terminal window; content goes into
  `#demoText` (filled by `type_text()`/direct `textContent` appends from
  Python).
- `editor.html`: a code-editor look (tab bar with a filename, CSS-counter
  line numbers, a highlighted-row style for newly added lines); content
  is driven entirely from Python via `helpers/editor_scene.py`.
- `demo.html`: the older split marketing-copy + code-window layout used
  by the `ide_typing_to_table` scenario.

Only change the Python side (the `*_scene.py` helper or the scenario
itself) if you're changing *what* is shown or *when* — not for pure
visual/color changes, which stay CSS-only.

### Real .sdoc syntax highlighting in the editor scene

`editor.html`'s content isn't hand-highlighted: `editor_scene.py` reuses
StrictDoc's own Pygments lexer
(`strictdoc.backend.rst.strictdoc_lexer.StrictDocLexer` — the same one
that highlights `.. code:: strictdoc` blocks in the docs) to tokenize
each `.sdoc` line, and reuses the product's own
`strictdoc/export/html/_static/pygments.css` for the token colors, so the
video's colors match the real product's highlighting. If StrictDoc's sdoc
grammar or its lexer's token colors change, this scene picks it up for
free — nothing here needs to be kept in sync by hand.

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

This starts StrictDoc at `http://127.0.0.1:5301` and keeps running until
stopped with Ctrl+C.

If the port is already taken by a previous run of this same demo server, it
is stopped automatically — no confirmation prompt. If it's taken by
anything else, the command refuses to touch it and hard-fails, printing
the occupying process(es) along with a `kill` command to stop them
yourself.

Scenario test runs use a separate port (`5302`, see `fixture.py`) so a
manual dev server can stay open while scenarios are (re)recorded.

### Read-only by default: nothing you do through the UI persists

By default, `invoke screencast-server` never serves the shared fixture
(or a generated scenario's project) directly. Instead, it builds a
disposable copy — fresh, from source, every time the command runs — and
serves that. Create documents, edit requirements, do whatever: the server
is a real live StrictDoc instance and genuinely writes to disk, but only
to that throwaway copy. Stop the server, run the command again, and
you're back to a clean starting point — nothing carries over, and the
shared fixture (which is checked into git) is never touched.

This is deliberate: the shared fixture at
`tests/screencast/fixtures/strictdoc-demo-project/` is committed to git.
Pointing a live server straight at it would mean any UI action taken
while "just looking" gets written into checked-in files for real.

### `--edit`: working on the real, persistent files instead

Pass `--edit` when you actually mean to change something on purpose —
curating the shared fixture's content, or picking up a generated
scenario's project where a previous manual session left it:

```bash
invoke screencast-server --edit
invoke screencast-server --focus=hello_world --edit
```

With `--edit`, the shared fixture case serves
`tests/screencast/fixtures/strictdoc-demo-project/` directly — anything
you do through the UI is a real, permanent edit to a checked-in file, and
will show up in `git status`. A generated scenario like `hello_world`
instead serves a persistent (but still gitignored) project that's reused
— not regenerated — across restarts, so manual edits survive a server
restart. Either way, `--edit` is the one flag that makes the server
write somewhere that outlives the current session; treat it as an
explicit, deliberate choice each time.

### Previewing a scenario that doesn't use the shared fixture

Some scenarios (e.g. `hello_world`) don't browse the shared fixture
project at all — they generate their own project from scratch (via a real
`strictdoc new` call). To preview one, pass `--focus=<scenario_name>`:

```bash
invoke screencast-server --focus=hello_world
```

This looks up `hello_world` in the `SCENARIOS` registry in
`tests/screencast/manual_scenarios.py` — the one place that knows this
particular scenario needs a real `strictdoc new` call to produce
something to serve — and serves the result (read-only by default, or
persistently with `--edit`, as above) on the same port/URL as the default
case (`http://127.0.0.1:5301`).

Everything a manual server ever writes lives under
`build/screencast_manual/<scenario_name>/{readonly,edit}/` — a disposable,
gitignored build artifact (see `/build/` in `.gitignore`), **not** a
fixture. Delete `build/screencast_manual/` (or a specific
scenario/mode's subdirectory) at any time to reset it back to a clean,
freshly generated state on the next run.

Note: the refusal of `strictdoc new` to overwrite existing project files
is that command's own, native behavior (see
`strictdoc/commands/new_command.py`), not something specific to
screencasts; `manual_scenarios.py` simply avoids triggering it by
skipping the call entirely once its target directory is already
populated (in `--edit` mode only — the read-only copy is always rebuilt
from scratch).

Adding a new scenario that needs this kind of on-demand project also means
adding an entry for it to the `SCENARIOS` registry in
`tests/screencast/manual_scenarios.py`, implementing both the read-only
and `--edit` cases.

## Adding a new scenario

1. Add fixture content under `fixtures/strictdoc-demo-project/`, if needed
   (or generate a project on the fly, like `hello_world` does with a real
   `strictdoc new` call — see "Previewing a scenario that doesn't use the
   shared fixture" above for what that means for manual preview).
2. Create `tests/screencast/scenarios/<scenario_name>/test_case.py` with a
   `Test.test(self, page)` method. Drive every click/type through a
   `Pointer` (see "Making clicks visible" above) rather than raw
   `page.click()`/`page.fill()`, and use the `helpers/` Page Objects (add
   new ones there if the scenario needs UI areas not covered yet). Insert
   `pause()` calls at the beats a viewer needs to register.
3. Run `invoke test-screencast --record-video --focus=<scenario_name>` to
   verify the recording.

Standalone HTML playground scenes (`demo.html`, `terminal.html`,
`editor.html` — see "Editing scene visuals" above) are filled from Python
via direct DOM manipulation (`textContent`/`innerHTML` appends), not real
keyboard/DOM input: `demo.html`/`terminal.html`'s typing effect only
*looks* like typing, it doesn't simulate keyboard input into a real
input, textarea, or code editor. Form fields on the live server, by
contrast, are typed into for real via `Pointer.type_into()`
(`press_sequentially`, real key events).
