# Screencast generator: move demo-video pipeline into StrictDoc

## WHAT

- Demo screencasts (`.webm` videos) can be generated entirely from within
  the StrictDoc repository, without depending on another repository or a
  separate checkout.
- The generator has no Node.js/npm dependency.
- Each demo scenario is an automated check that:
  - passes or fails according to whether it still reflects real, current
    UI behavior, and
  - can optionally run in a recording mode that (re)generates the
    scenario's video.
- A failing scenario means its video can no longer be trusted and must be
  reviewed before being re-recorded.
- Screencast scenarios run independently from the main end-to-end test
  suite, without being folded into it.
- Each scenario runs against a real, live instance of the application.
- The project used for recording is self-contained within the repository.
- Delivering generated videos to the product website is OUT OF SCOPE for
  this task; this task only produces the videos within the StrictDoc
  repository.

## WHY

StrictDoc needs a maintainable way to generate product demo videos that stay
synchronized with the actual UI.

Video scenarios should live next to the features they demonstrate and run
through the same automation pipeline as UI tests.

A single scenario definition can then serve both as a source for generating
videos and as a regression check for the demonstrated workflow.

## HOW

- **Language**: the generator is written in Python using the Playwright
  Python API (`playwright.sync_api`), including `record_video_dir` for
  video capture. No Node.js/npm dependency exists in the project.
- **Server lifecycle**: scenarios start/stop a real StrictDoc server through
  `tests/end2end/server.py::SDocTestServer`, in-process to this repository.
- **Scenario structure**: each demo scene is its own pytest test case,
  following the `tests/end2end/screens/*/test_case.py` convention.
  Playwright-native Page Object helpers live under
  `tests/screencast/helpers/` (e.g. `Screen`, `ViewTypeSelector`), for reuse
  across screencast scenarios and as a foundation for a wider Playwright
  suite later. Standalone HTML/IDE-style scenes (fake typing effect) use a
  local HTML playground (`demo.html`).
- **Dual-purpose run modes**:
  - default run: scenario executes as a normal pass/fail check, fast, with
    no video output;
  - recording run: the `--strictdoc-record-video` pytest option makes the
    same scenario also capture and save a `.webm` to
    `tests/screencast/output/`.
- **Invoke task**: `invoke test-screencast` (alias `tsc`) in `tasks.py`,
  following the conventions of `test_end2end`/`test_unit_server` (focus
  filter, junit output under `TEST_REPORTS_DIR`). Kept separate from
  `invoke test-end2end`: screencast runs are slower and produce binary
  artifacts.
- **Dependencies**: `playwright` (Python package) is a `check`-environment
  dependency (`requirements.check.txt`); the Chromium browser binary is
  installed separately via `playwright install chromium`.
- **Fixtures**: `tests/screencast/fixtures/strictdoc-demo-project/` is the
  demo content used by scenarios, shaped like other `tests/end2end`
  fixtures.
- **Out of scope**: publishing/copying generated `.webm` files to
  `strictdoc-project.github.io`; migrating the rest of the e2e suite off
  SeleniumBase (a separate, future initiative).
