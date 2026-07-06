from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

STRICTDOC_ROOT = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.isdir(STRICTDOC_ROOT), STRICTDOC_ROOT
sys.path.insert(0, STRICTDOC_ROOT)

import psutil  # noqa: E402

from tests.end2end.server import SDocTestServer  # noqa: E402
from tests.screencast.fixture import DEV_SERVER_PORT  # noqa: E402
from tests.screencast.manual_scenarios import (  # noqa: E402
    DEFAULT_SCENARIO,
    SCENARIOS,
)


def find_pids_on_port(port: int) -> list[int]:
    result = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [int(pid) for pid in result.stdout.split()]


def describe_process(pid: int) -> str:
    try:
        cmdline = " ".join(psutil.Process(pid).cmdline())
    except psutil.NoSuchProcess:
        return f"PID {pid} (no longer running)"
    return f"PID {pid}: {cmdline}"


def is_previous_demo_server(pid: int) -> bool:
    try:
        cmdline = " ".join(psutil.Process(pid).cmdline())
    except psutil.NoSuchProcess:
        return False
    # Matched by shape (any strictdoc server bound to this dev port), not by
    # project directory: --focus can point at a different project per run.
    return (
        "strictdoc.cli.main" in cmdline
        and "server" in cmdline
        and f"--port {DEV_SERVER_PORT}" in cmdline
    )


def collect_pid_tree(pid: int) -> list[int]:
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return [pid]
    return [pid] + [child.pid for child in process.children(recursive=True)]


def free_dev_port(port: int) -> None:
    """
    If `port` is occupied by a previous run of this same demo server
    (matched by the fixture path in its command line), stop it. If it's
    occupied by anything else, raise instead of touching it.
    """

    pids = find_pids_on_port(port)
    if not pids:
        return

    foreign_pids = [pid for pid in pids if not is_previous_demo_server(pid)]
    if foreign_pids:
        details = "\n".join(f"  {describe_process(pid)}" for pid in foreign_pids)

        pid_tree: list[int] = []
        for pid in foreign_pids:
            pid_tree.extend(collect_pid_tree(pid))

        kill_command = "kill " + " ".join(str(pid) for pid in pid_tree)
        force_kill_command = "kill -9 " + " ".join(str(pid) for pid in pid_tree)
        raise OSError(
            f"Port {port} is occupied by another process, not a previous "
            f"run of this demo server:\n{details}\n"
            "Stop it yourself if you want to reuse this port, e.g.:\n"
            f"  {kill_command}\n"
            "If it doesn't respond (e.g. it has an active reloader "
            "process), force it:\n"
            f"  {force_kill_command}"
        )

    for pid in pids:
        print(  # noqa: T201
            f"🔁 Stopping a previous demo server on port {port} ({pid})."
        )
        try:
            psutil.Process(pid).terminate()
        except psutil.NoSuchProcess:
            continue

    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if not find_pids_on_port(port):
            return
        time.sleep(0.1)

    for pid in find_pids_on_port(port):
        try:
            psutil.Process(pid).kill()
        except psutil.NoSuchProcess:
            continue


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--focus",
        default=DEFAULT_SCENARIO,
        choices=sorted(SCENARIOS),
        help=(
            "Which screencast scenario's project to serve "
            f"(default: {DEFAULT_SCENARIO})."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        project_dir, config_path = SCENARIOS[args.focus]()

        free_dev_port(DEV_SERVER_PORT)

        with SDocTestServer(
            input_path=str(project_dir),
            config_path=str(config_path) if config_path is not None else None,
            port=DEV_SERVER_PORT,
        ) as server:
            print(  # noqa: T201
                f"🚀 StrictDoc demo server ({args.focus}): "
                f"{server.get_host_and_port()}"
            )
            print("   Press Ctrl+C to stop.")  # noqa: T201

            server.process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Stopping StrictDoc demo server.")  # noqa: T201

    except OSError as error:
        print(error, file=sys.stderr)  # noqa: T201
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
