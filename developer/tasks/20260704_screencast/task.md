# Screencast generator: move demo-video pipeline into StrictDoc

## WHAT

StrictDoc's product website needs demo screencasts (`.webm` videos) that show
real, up-to-date UI behavior (web UI, CLI, IDE-style scenes). The pipeline
that produces these videos must live inside the StrictDoc repository so it
stays in sync with the actual product, and it must double as a regression
signal: if a recorded scenario fails, the corresponding published video is
considered outdated.

Success criteria:

- A `tests/screencast/` sub-project exists in the StrictDoc repository,
  written in Python, with no Node.js/npm dependency.
- Each demo scenario is expressed as a scenario/test case that:
  - passes or fails like a regular automated check (usable as a staleness
    signal for the corresponding video), and
  - can optionally be run in "recording" mode to (re)generate the
    corresponding `.webm` video file.
- A dedicated `invoke` task (e.g. `invoke test-screencast`) runs the
  screencast scenarios; it is not folded into `invoke test-end2end`.
- The scenario harness starts and stops a real StrictDoc server itself
  (in-process to the repository, no dependency on a sibling checkout or a
  separate `tox` invocation of another repo).
- The demo fixture project used for recording is checked into
  `tests/screencast/fixtures/`, cleaned of unrelated build/cache artifacts.
- Delivery of generated videos to the product website
  (`strictdoc-project.github.io`) is explicitly OUT OF SCOPE for this task;
  this task only produces the videos inside the StrictDoc repository.

## WHY

The video generator currently lives in the `strictdoc-project.github.io`
(Hugo) repository and drives a *separate* StrictDoc checkout via `tox` to
record scenes. This means:

- videos can silently go stale after StrictDoc UI changes, with no signal;
- the generator's environment assumptions (sibling checkout, `tox` on PATH,
  hardcoded Python version) are fragile and only make sense from outside the
  StrictDoc repo;
- introducing new demo scenarios or updating them requires cross-repo
  coordination instead of living next to the code it demonstrates.

Moving the generator into StrictDoc, and expressing scenarios as ordinary
test cases, ties video freshness directly to the same CI/dev signal already
used for UI regressions, and lets one scenario definition serve both as a
regression check and as a video source.

## HOW

### Current state (starting point, not a spec)

`tests/screencast/` currently holds a raw copy of the website repo's
generator: `demo.js` (Playwright JS, defines scenes as a JSON-like step list
and renders `.webm` via `context.newContext({ recordVideo })`),
`strictdoc_server.py`/`run_server.py`/`run_demo.py` (spawns StrictDoc through
`tox -e py310-development` against a *sibling* `../strictdoc` checkout), and
a copy of the `strictdoc-demo-project` fixture (including stray
`__pycache__`/`.DS_Store`/cache build output). This code is a starting point
to adapt, not a design to preserve as-is.

### Target design

- **Language**: rewrite the generator in Python using the Playwright Python
  API (`playwright.sync_api`), including `record_video_dir` for video
  capture. Drop `demo.js`, `package.json`, `package-lock.json`,
  `node_modules` — no Node.js/npm dependency remains in the project.
- **Server lifecycle**: reuse the existing, already-hardened
  `tests/end2end/server.py::SDocTestServer` (or a thin adaptation of it)
  to start/stop a StrictDoc server directly via
  `python -m strictdoc.cli.main server ...` in-process to this repository —
  no `tox` subprocess, no assumption of a sibling checkout.
- **Scenario structure**: each demo scene becomes its own pytest test case,
  following the existing `tests/end2end/screens/*/test_case.py` convention.
  The existing `Screen_*` / `helpers/components/*` Page Object classes are
  tied to SeleniumBase (`BaseCase`, `By.XPATH`) and cannot be called
  directly from Playwright code — instead, new Playwright-native Page
  Object helpers are introduced under `tests/screencast/helpers/`, mirroring
  the existing helpers' names/selectors/responsibilities (verified against
  the actually rendered UI and the existing SeleniumBase tests, which
  describe real current UI behavior). These new helpers are written for
  reuse across the screencast suite now, and as a base for a wider
  Playwright suite later, not as one-off inline locators per test.
  Standalone HTML/IDE-style scenes (fake typing effect) keep using a local
  HTML playground, driven from Python instead of `demo.js`.
- **Dual-purpose run modes**:
  - default run: scenario executes as a normal pass/fail check (fast, no
    video output) — a failure means the scenario (and its published video)
    is stale;
  - recording run: an explicit flag/env var (e.g.
    `--strictdoc-record-video`) makes the same scenario also capture and
    save a `.webm` to `tests/screencast/output/`.
- **Invoke task**: add `invoke test-screencast` (with a short alias) in
  `tasks.py`, following the conventions of `test_end2end`/`test_unit_server`
  (headless option, focus filter, junit output under `TEST_REPORTS_DIR`).
  Kept separate from `invoke test-end2end` since screencast runs are
  slower/heavier and produce binary artifacts.
- **Dependencies**: add `playwright` (Python package) to `pyproject.toml` as
  a dev/test dependency; document the `playwright install chromium` setup
  step (Chromium only, matching current generator's needs).
- **Fixtures**: keep `strictdoc-demo-project` as the demo content, but strip
  `__pycache__`, `.DS_Store`, and any generated `output/_cache` before
  committing, aligning its shape with other `tests/end2end` fixtures.
- **Out of scope**: publishing/copying generated `.webm` files to
  `strictdoc-project.github.io`; migrating the rest of the e2e suite off
  SeleniumBase (future direction, only considered here to avoid decisions
  that would conflict with it, not implemented).

### Working agreement for this task

Implementation proceeds in discrete stages; each stage stops for review and
a commit before starting the next. Open questions encountered during
implementation are raised with the user first rather than resolved by
assumption or open-ended codebase research, unless the user asks for deeper
investigation.
