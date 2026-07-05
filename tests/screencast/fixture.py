from __future__ import annotations

from pathlib import Path

SCREENCAST_DIR = Path(__file__).resolve().parent

FIXTURE_DIR = SCREENCAST_DIR / "fixtures" / "strictdoc-demo-project"
FIXTURE_CONFIG = FIXTURE_DIR / "strictdoc_config.py"

OUTPUT_DIR = SCREENCAST_DIR / "output"

# Manual dev server: kept open while developing/inspecting a scene in the
# browser.
#
# Deliberately outside both StrictDoc's own default server port (5111) and
# the tests/end2end server port range (5112-5212), so this doesn't collide
# with `invoke server` or the end2end test suite.
DEV_SERVER_PORT = 5301

# Recording server: a separate port so a manual dev server (above) can stay
# open while scenarios are (re)recorded.
RECORD_SERVER_PORT = 5302
