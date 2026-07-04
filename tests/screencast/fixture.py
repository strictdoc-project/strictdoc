from __future__ import annotations

from pathlib import Path

SCREENCAST_DIR = Path(__file__).resolve().parent

FIXTURE_DIR = SCREENCAST_DIR / "fixtures" / "strictdoc-demo-project"
FIXTURE_CONFIG = FIXTURE_DIR / "strictdoc_config.py"

# Manual dev server: kept open while developing/inspecting a scene in the
# browser.
DEV_SERVER_PORT = 5111

# Recording server: a separate port so a manual dev server (above) can stay
# open while scenarios are (re)recorded.
RECORD_SERVER_PORT = 5112
