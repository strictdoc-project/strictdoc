"""
Unit tests for tools/server_check.py: detecting who occupies a port, and
safely stopping only strictdoc's own server process tree while leaving
unrelated processes alone.

These fake `lsof`/`ps`/`pgrep`/`kill` instead of touching real OS
processes, so they run the exact same branching logic that `invoke server`
uses when its port is already taken.
"""

from __future__ import annotations

import subprocess

import pytest

from tools import server_check


class FakeProcessTree:
    """
    Fakes the `lsof`/`ps`/`pgrep` commands server_check.py shells out to,
    for a small hand-built set of PIDs, parents, and children.
    """

    def __init__(self) -> None:
        self.port_pids: list[int] = []
        self.commands: dict[int, str] = {}
        self.parents: dict[int, int] = {}
        self.children: dict[int, list[int]] = {}
        self.killed: list[tuple[int, int]] = []
        self.dead: set = set()

    def run(self, cmd: list[str], **_kwargs) -> subprocess.CompletedProcess:
        if cmd[0] == "lsof":
            stdout = "\n".join(str(pid) for pid in self.port_pids)
            return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")

        if cmd[0] == "ps" and cmd[-1] == "command=":
            pid = int(cmd[2])
            return subprocess.CompletedProcess(
                cmd, 0, stdout=self.commands.get(pid, ""), stderr=""
            )

        if cmd[0] == "ps" and cmd[-1] == "ppid=":
            pid = int(cmd[2])
            parent = self.parents.get(pid)
            return subprocess.CompletedProcess(
                cmd, 0, stdout=str(parent) if parent else "", stderr=""
            )

        if cmd[0] == "pgrep":
            pid = int(cmd[2])
            kids = self.children.get(pid, [])
            return subprocess.CompletedProcess(
                cmd,
                0 if kids else 1,
                stdout="\n".join(str(kid) for kid in kids),
                stderr="",
            )

        raise AssertionError(f"unexpected command: {cmd}")

    def kill(self, pid: int, sig: int) -> None:
        self.killed.append((pid, sig))
        if sig == 0:
            if pid in self.dead:
                raise ProcessLookupError
            return
        self.dead.add(pid)


@pytest.fixture
def fake_tree(monkeypatch) -> FakeProcessTree:
    tree = FakeProcessTree()
    monkeypatch.setattr(server_check.subprocess, "run", tree.run)
    monkeypatch.setattr(server_check.os, "kill", tree.kill)
    monkeypatch.setattr(server_check.time, "sleep", lambda _seconds: None)
    return tree


def fake_input(answer: str):
    def _input(prompt: str = "") -> str:
        print(prompt, end="")  # noqa: T201
        return answer

    return _input


def test_is_strictdoc_server_pid_detects_via_ancestor(fake_tree):
    fake_tree.commands[300] = (
        "/path/python -m strictdoc.cli.main --debug server . --reload"
    )
    fake_tree.commands[301] = (
        "/path/python -c "
        "from multiprocessing.spawn import spawn_main; spawn_main()"
    )
    fake_tree.parents[301] = 300

    assert server_check.is_strictdoc_server_pid(300) is True
    assert server_check.is_strictdoc_server_pid(301) is True


def test_is_strictdoc_server_pid_false_for_unrelated_process(fake_tree):
    fake_tree.commands[400] = "/usr/bin/python3 -m http.server 5111"

    assert server_check.is_strictdoc_server_pid(400) is False


def test_free_strictdoc_port_when_port_is_free(fake_tree):
    fake_tree.port_pids = []

    assert server_check.free_strictdoc_port(5111) is True
    assert fake_tree.killed == []


def test_free_strictdoc_port_refuses_foreign_process(fake_tree):
    fake_tree.port_pids = [111]
    fake_tree.commands[111] = "/usr/bin/python3 -m http.server 5111"

    with pytest.raises(OSError) as excinfo:
        server_check.free_strictdoc_port(5111)

    message = str(excinfo.value)
    assert "occupied by another process" in message
    assert "PID 111" in message
    assert fake_tree.killed == []


def test_free_strictdoc_port_own_server_keep_existing(fake_tree, monkeypatch):
    fake_tree.port_pids = [200]
    fake_tree.commands[200] = (
        "/path/python -m strictdoc.cli.main --debug server . "
        "--host 127.0.0.1 --reload --watch"
    )
    monkeypatch.setattr("builtins.input", fake_input("n"))

    result = server_check.free_strictdoc_port(5111)

    assert result is False
    assert fake_tree.killed == []


def test_free_strictdoc_port_own_server_replace(fake_tree, monkeypatch):
    fake_tree.port_pids = [200]
    fake_tree.commands[200] = (
        "/path/python -m strictdoc.cli.main --debug server . "
        "--host 127.0.0.1 --reload --watch"
    )
    fake_tree.children[200] = [201]
    fake_tree.commands[201] = (
        "/path/python -c "
        "from multiprocessing.spawn import spawn_main; spawn_main()"
    )
    monkeypatch.setattr("builtins.input", fake_input("y"))

    result = server_check.free_strictdoc_port(5111)

    assert result is True
    assert (200, server_check.signal.SIGTERM) in fake_tree.killed
    assert (201, server_check.signal.SIGTERM) in fake_tree.killed
