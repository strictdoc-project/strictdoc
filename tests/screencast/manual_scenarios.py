"""
Registry of screencast scenarios that can be previewed manually in a real
browser via `invoke screencast-server --focus=<scenario>` (see
tests/screencast/run_server.py and README.md).

Each entry resolves (given `editable`) to a project directory to serve,
plus an optional config path (None if the project carries its own
strictdoc_config.py):

- `editable=False` (the default): a disposable copy, freshly rebuilt from
  source on every call. Anything done through the UI is discarded the
  next time the server is (re)started — nothing you do here can affect
  the shared fixture or a previous manual session.
- `editable=True` (`--edit`): the scenario's real, persistent files —
  the checked-in shared fixture itself, or a generated project that's
  reused (not regenerated) across restarts. Changes made through the UI
  are real and stick around. Opt in deliberately, when curating fixture
  content is the point.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from tests.screencast.fixture import (
    FIXTURE_CONFIG,
    FIXTURE_DIR,
    MANUAL_SERVER_BUILD_DIR,
)
from tests.screencast.scenarios.hello_world.test_case import run_strictdoc_new

DEFAULT_SCENARIO = "fixture"

ScenarioSetup = Callable[[bool], Tuple[Path, Optional[Path]]]


def _prepare_fixture_project(editable: bool) -> Tuple[Path, Optional[Path]]:
    if editable:
        return FIXTURE_DIR, FIXTURE_CONFIG

    project_dir = MANUAL_SERVER_BUILD_DIR / "fixture" / "readonly"
    if project_dir.exists():
        shutil.rmtree(project_dir)
    shutil.copytree(FIXTURE_DIR, project_dir)
    return project_dir, project_dir / "strictdoc_config.py"


def _prepare_hello_world_project(editable: bool) -> Tuple[Path, Optional[Path]]:
    if editable:
        project_dir = MANUAL_SERVER_BUILD_DIR / "hello_world" / "edit"
        # strictdoc_config.py is the last file `strictdoc new` writes: its
        # presence means a previous run already completed successfully.
        # Skip regenerating so manual edits made through the UI survive
        # server restarts, and so we don't hit `strictdoc new`'s refusal
        # to overwrite existing files (see README.md).
        if not (project_dir / "strictdoc_config.py").exists():
            run_strictdoc_new(project_dir)
        return project_dir, None

    project_dir = MANUAL_SERVER_BUILD_DIR / "hello_world" / "readonly"
    if project_dir.exists():
        shutil.rmtree(project_dir)
    run_strictdoc_new(project_dir)
    return project_dir, None


SCENARIOS: Dict[str, ScenarioSetup] = {
    "fixture": _prepare_fixture_project,
    "hello_world": _prepare_hello_world_project,
}
