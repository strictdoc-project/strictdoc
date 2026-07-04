from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parents[1]
DEFAULT_STRICTDOC_ROOT = REPO_ROOT / "strictdoc"

STRICTDOC_ROOT = Path(
    os.environ.get("STRICTDOC_ROOT", DEFAULT_STRICTDOC_ROOT)
).resolve()

FIXTURE_DIR = DEMO_DIR / "fixtures" / "strictdoc-demo-project"
FIXTURE_CONFIG = FIXTURE_DIR / "strictdoc_config.py"

SERVER_URL = os.environ.get("STRICTDOC_SITE_URL", "http://127.0.0.1:5111/")
VIDEO_SERVER_URL = os.environ.get(
    "STRICTDOC_VIDEO_SITE_URL", "http://127.0.0.1:5112/"
)

STRICTDOC_PYTHON_VERSION = os.environ.get(
    "STRICTDOC_PYTHON_VERSION", "3.10.16"
)


def resolve_tox() -> Path | None:
    # Order: explicit override, PATH, pyenv guess (for setups without pyenv shims on PATH).
    env_override = os.environ.get("STRICTDOC_TOX")
    if env_override:
        return Path(env_override).resolve()

    on_path = shutil.which("tox")
    if on_path:
        return Path(on_path).resolve()

    pyenv_guess = (
        Path.home()
        / ".pyenv"
        / "versions"
        / STRICTDOC_PYTHON_VERSION
        / "bin"
        / "tox"
    )
    if pyenv_guess.exists():
        return pyenv_guess.resolve()

    return None


STRICTDOC_TOX = resolve_tox()


def is_server_available(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1):
            return True
    except Exception:
        return False


def get_port_from_url(url: str) -> int:
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.port is None:
        if parsed_url.scheme == "https":
            return 443
        return 80
    return parsed_url.port


def find_processes_on_port(port: int) -> list[int]:
    result = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return []

    return [int(pid) for pid in result.stdout.splitlines() if pid.strip()]


def stop_existing_server(url: str) -> None:
    port = get_port_from_url(url)
    process_ids = find_processes_on_port(port)

    if not process_ids:
        return

    print(f"⚠️  StrictDoc server URL is already in use: {url}", file=sys.stderr)
    print(
        f"   Stopping existing process(es) on port {port}: "
        f"{', '.join(str(pid) for pid in process_ids)}",
        file=sys.stderr,
    )

    for process_id in process_ids:
        os.kill(process_id, signal.SIGTERM)

    started_at = time.time()
    while time.time() - started_at < 10:
        if not find_processes_on_port(port):
            return
        time.sleep(0.2)

    for process_id in find_processes_on_port(port):
        os.kill(process_id, signal.SIGKILL)


def start_server(url: str = SERVER_URL) -> subprocess.Popen:
    if not STRICTDOC_ROOT.exists():
        raise RuntimeError(
            f"❌  StrictDoc repository not found: {STRICTDOC_ROOT}\n"
            "   Set STRICTDOC_ROOT to the path of your strictdoc checkout."
        )

    if STRICTDOC_TOX is None:
        raise RuntimeError(
            "❌  tox not found on PATH and no pyenv fallback matched.\n"
            "   Install tox (e.g. `pip install tox`) so it's on PATH, or set "
            "STRICTDOC_TOX to its executable path."
        )

    stop_existing_server(url)

    port = get_port_from_url(url)
    host = urllib.parse.urlparse(url).hostname or "127.0.0.1"

    env = os.environ.copy()
    env["PYENV_VERSION"] = STRICTDOC_PYTHON_VERSION

    return subprocess.Popen(
        [
            str(STRICTDOC_TOX),
            "-e",
            "py310-development",
            "--",
            "python",
            "-m",
            "strictdoc.cli.main",
            "--debug",
            "server",
            str(FIXTURE_DIR),
            "--config",
            str(FIXTURE_CONFIG),
            "--host",
            host,
            "--port",
            str(port),
            "--reload",
        ],
        cwd=STRICTDOC_ROOT,
        env=env,
        start_new_session=True,
    )


def wait_for_server(
    url: str, server: subprocess.Popen, timeout_seconds: int = 180
) -> None:
    started_at = time.time()

    while time.time() - started_at < timeout_seconds:
        if is_server_available(url):
            return

        if server.poll() is not None:
            raise RuntimeError(
                "❌  StrictDoc server process exited before becoming available: "
                f"exit code {server.returncode}"
            )

        time.sleep(0.5)

    raise RuntimeError(
        f"⏳  Timed out waiting for StrictDoc server after {timeout_seconds}s: {url}"
    )


def stop_server(server: subprocess.Popen) -> None:
    if server.poll() is not None:
        return

    try:
        os.killpg(server.pid, signal.SIGTERM)
        server.wait(timeout=10)
    except ProcessLookupError:
        return
    except subprocess.TimeoutExpired:
        try:
            os.killpg(server.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
