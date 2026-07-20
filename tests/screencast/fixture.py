from __future__ import annotations

from pathlib import Path

SCREENCAST_DIR = Path(__file__).resolve().parent
STRICTDOC_ROOT = SCREENCAST_DIR.parent.parent

FIXTURE_DIR = SCREENCAST_DIR / "fixtures" / "strictdoc-demo-project"
FIXTURE_CONFIG = FIXTURE_DIR / "strictdoc_config.py"

OUTPUT_DIR = SCREENCAST_DIR / "output"

# Disposable projects generated on demand for `invoke screencast-server
# --focus=<scenario>` (e.g. by running a scenario's real CLI commands).
# Not checked into git (see /build/ in .gitignore). Left in place between
# runs so a scenario's setup doesn't rerun (and clobber manual edits) every
# time the manual server is restarted; delete the directory to reset it.
MANUAL_SERVER_BUILD_DIR = STRICTDOC_ROOT / "build" / "screencast_manual"

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
