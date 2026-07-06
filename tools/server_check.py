"""
Checks whether a port is occupied by a previous strictdoc.cli.main server
process (walking process ancestry, so a --reload supervisor's
multiprocessing worker/tracker children count too), and offers to stop it.
A foreign (non-strictdoc) process on the port is never touched
automatically.

Used by `invoke server` (see tasks.py) before starting a new server.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time

BOLD = "\033[1m"
RESET = "\033[0m"


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


def describe_pid(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        check=False,
        capture_output=True,
        text=True,
    )
    command = result.stdout.strip()
    return command if command else "(no longer running)"


def get_ppid(pid: int) -> int | None:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "ppid="],
        check=False,
        capture_output=True,
        text=True,
    )
    text = result.stdout.strip()
    return int(text) if text else None


def command_is_strictdoc_server(command: str) -> bool:
    return "strictdoc.cli.main" in command and " server " in f" {command} "


def is_strictdoc_server_pid(pid: int) -> bool:
    """
    True if `pid` is a strictdoc.cli.main server process, or a descendant
    of one (e.g. a --reload supervisor's multiprocessing worker/tracker,
    which doesn't have "strictdoc.cli.main" in its own command line but is
    still part of that server's process tree).
    """

    current: int | None = pid
    for _ in range(10):
        if current is None or current <= 1:
            return False
        if command_is_strictdoc_server(describe_pid(current)):
            return True
        current = get_ppid(current)
    return False


def collect_pid_tree(pid: int) -> list[int]:
    result = subprocess.run(
        ["pgrep", "-P", str(pid)],
        check=False,
        capture_output=True,
        text=True,
    )
    children = [int(child_pid) for child_pid in result.stdout.split()]
    pids = [pid]
    for child_pid in children:
        pids.extend(collect_pid_tree(child_pid))
    return pids


def pid_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def stop_pids(pids: list[int]) -> None:
    all_pids: list[int] = []
    for pid in pids:
        all_pids.extend(collect_pid_tree(pid))

    for pid in all_pids:
        print(f"  ⏹️  stopping PID {pid} ({describe_pid(pid)})")  # noqa: T201
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue

    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if not any(pid_is_alive(pid) for pid in all_pids):
            return
        time.sleep(0.1)

    for pid in all_pids:
        if pid_is_alive(pid):
            print(f"  ⚠️  {pid} did not stop, sending SIGKILL")  # noqa: T201
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                continue


def free_strictdoc_port(port: int) -> bool:
    """
    If `port` is occupied by a previous strictdoc.cli.main server process,
    ask whether to stop it (and its child processes) and returns whether
    the caller should proceed with starting a new server. If it's occupied
    by anything else, raise instead of touching it.
    """

    pids = find_pids_on_port(port)
    if not pids:
        return True

    foreign_pids = [pid for pid in pids if not is_strictdoc_server_pid(pid)]
    if foreign_pids:
        details = "\n".join(
            f"  PID {pid}: {describe_pid(pid)}" for pid in foreign_pids
        )
        raise OSError(
            f"⚠️  Port {port} is occupied by another process, not a "
            f"strictdoc server:\n{details}\n"
            "Stop it yourself if you want to reuse this port."
        )

    details = "\n".join(f"  PID {pid}: {describe_pid(pid)}" for pid in pids)
    print(  # noqa: T201
        f"🔁 A previous strictdoc server is running on port {port}:\n{details}"
    )
    answer = (
        input(f"{BOLD}Stop it and start a new one? [y/n]:{RESET} ")
        .strip()
        .lower()
    )
    if answer != "y":
        print(  # noqa: T201
            f"ℹ️  Keeping the existing server on port {port}. Not starting a new one."
        )
        return False

    stop_pids(pids)
    return True
