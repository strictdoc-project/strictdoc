"""
Registry of screencast scenarios that can be previewed manually in a real
browser via `invoke screencast-server --focus=<scenario>` (see
tests/screencast/run_server.py and README.md).

Each entry resolves to a project directory to serve, plus an optional
config path (None if the project carries its own strictdoc_config.py).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from tests.screencast.fixture import (
    FIXTURE_CONFIG,
    FIXTURE_DIR,
    MANUAL_SERVER_BUILD_DIR,
)
from tests.screencast.scenarios.hello_world.test_case import run_strictdoc_new

DEFAULT_SCENARIO = "fixture"

ScenarioSetup = Callable[[], Tuple[Path, Optional[Path]]]


def _prepare_fixture_project() -> Tuple[Path, Optional[Path]]:
    return FIXTURE_DIR, FIXTURE_CONFIG


def _prepare_hello_world_project() -> Tuple[Path, Optional[Path]]:
    project_dir = MANUAL_SERVER_BUILD_DIR / "hello_world"

    # strictdoc_config.py is the last file `strictdoc new` writes: its
    # presence means a previous run already completed successfully. Skip
    # regenerating so manual edits made through the UI survive server
    # restarts, and so we don't hit `strictdoc new`'s refusal to overwrite
    # existing files.
    if not (project_dir / "strictdoc_config.py").exists():
        run_strictdoc_new(project_dir)

    return project_dir, None


SCENARIOS: Dict[str, ScenarioSetup] = {
    "fixture": _prepare_fixture_project,
    "hello_world": _prepare_hello_world_project,
}
