"""
A fork server that starts the StrictDoc test servers of one pytest process.

Most of the start time of a StrictDoc server is Python imports. The fork
server is a helper process that imports StrictDoc, its web server, and
uvicorn once. For each end-to-end test, it forks a child process, and the
child runs the same command line as "python -m strictdoc.cli.main server ...".
Each test still gets its own server process, with its own working directory
and state, but without the import time.

The fork server works only on Linux and macOS, because Windows has no fork().
SDocTestServer starts the server with subprocess.Popen when the fork server is
not available.

Protocol: the client sends one request per server over a Unix socket pair:
a JSON line with the command line arguments and the working directory, and
two file descriptors, the stdout log file and the write end of the stderr pipe.
The fork server answers with a JSON line with the process ID of the child.

@relation(SDOC-SRS-46, scope=file)
"""

import json
import os
import signal
import socket
import subprocess
import sys
from typing import Any, Dict, List, Optional

import psutil

# The modules that the fork server imports before it forks the first child.
# These are the modules that a "strictdoc server" process imports at startup.
PRELOADED_MODULES = (
    "strictdoc.cli.main",
    "strictdoc.commands.server",
    "strictdoc.server.app",
    "strictdoc.server.routers.main_router",
    "strictdoc.server.routers.other_router",
    "strictdoc.server.server",
    "uvicorn",
)

READY_MESSAGE = b"ready\n"
MAX_MESSAGE_SIZE = 65536


class ForkedServerProcess:
    """
    The part of the subprocess.Popen interface that SDocTestServer uses, for a
    server process that the fork server started.

    The fork server, not the test process, is the parent of the server
    process. So wait() polls the process with psutil instead of os.waitpid().
    """

    def __init__(self, pid: int, stderr: Any) -> None:
        self.pid: int = pid
        self.stderr = stderr

    def send_signal(self, signal_: int) -> None:
        try:
            os.kill(self.pid, signal_)
        except ProcessLookupError:
            pass

    def terminate(self) -> None:
        self.send_signal(signal.SIGTERM)

    def wait(self, timeout: Optional[float] = None) -> None:
        try:
            psutil.Process(self.pid).wait(timeout=timeout)
        except psutil.NoSuchProcess:
            pass
        except psutil.TimeoutExpired as exception_:
            raise subprocess.TimeoutExpired(
                cmd=f"pid {self.pid}", timeout=timeout or 0
            ) from exception_


class ForkServerClient:
    def __init__(self, environment: Dict[str, str]) -> None:
        self.environment: Dict[str, str] = environment
        client_socket, server_socket = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_STREAM
        )
        self.socket: socket.socket = client_socket
        self.process = subprocess.Popen(
            [
                sys.executable,
                os.path.abspath(__file__),
                str(server_socket.fileno()),
            ],
            pass_fds=[server_socket.fileno()],
            stdin=subprocess.DEVNULL,
            env=environment,
        )
        server_socket.close()
        self.reader = self.socket.makefile("rb")
        ready_line = self.reader.readline()
        if ready_line != READY_MESSAGE:
            self.close()
            raise OSError(
                "ForkServerClient: the fork server did not start: "
                f"{ready_line!r}."
            )

    def is_compatible(self, environment: Dict[str, str]) -> bool:
        """
        A forked server keeps the environment of the fork server, so a request
        must use the same environment. pytest changes PYTEST_CURRENT_TEST for
        every test, and the StrictDoc server does not read it.
        """
        return _without_volatile_variables(
            environment
        ) == _without_volatile_variables(self.environment)

    def start_server(
        self, args: List[str], cwd: str, stdout_fd: int
    ) -> ForkedServerProcess:
        stderr_read_fd, stderr_write_fd = os.pipe()
        try:
            request = json.dumps({"args": args, "cwd": cwd}).encode() + b"\n"
            socket.send_fds(
                self.socket, [request], [stdout_fd, stderr_write_fd]
            )
        finally:
            os.close(stderr_write_fd)
        response_line = self.reader.readline()
        if len(response_line) == 0:
            os.close(stderr_read_fd)
            raise OSError("ForkServerClient: the fork server has exited.")
        pid = json.loads(response_line)["pid"]
        return ForkedServerProcess(
            pid=pid, stderr=os.fdopen(stderr_read_fd, "rb")
        )

    def is_alive(self) -> bool:
        return self.process.poll() is None

    def close(self) -> None:
        # The fork server exits when its socket is closed.
        self.reader.close()
        self.socket.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()


def _without_volatile_variables(environment: Dict[str, str]) -> Dict[str, str]:
    return {
        name_: value_
        for name_, value_ in environment.items()
        if name_ != "PYTEST_CURRENT_TEST"
    }


def _run_child(
    *, control_socket: socket.socket, request: Dict[str, Any], fds: List[int]
) -> None:
    """
    Runs in the forked child. Never returns.
    """
    exit_code = 0
    try:
        control_socket.close()
        # The fork server ignores SIGCHLD to reap its children. The StrictDoc
        # server must wait for its own subprocesses, so restore the default.
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        stdout_fd, stderr_fd = fds
        os.dup2(stdout_fd, 1)
        os.dup2(stderr_fd, 2)
        os.close(stdout_fd)
        os.close(stderr_fd)
        os.chdir(request["cwd"])
        # "python -m" puts the working directory first on sys.path.
        sys.path.insert(0, request["cwd"])
        sys.argv = list(request["args"])

        from strictdoc.cli.main import main  # noqa: PLC0415

        main()
    except SystemExit as exception_:
        exit_code = exception_.code if isinstance(exception_.code, int) else 1
    except BaseException:  # noqa: BLE001
        import traceback  # noqa: PLC0415

        traceback.print_exc()
        exit_code = 1
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            os._exit(exit_code)


def serve(control_socket_fd: int) -> None:
    import importlib  # noqa: PLC0415

    for module_name_ in PRELOADED_MODULES:
        importlib.import_module(module_name_)

    # The children exit on their own. Ignoring SIGCHLD makes the kernel reap
    # them, so they do not stay as zombie processes.
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    control_socket = socket.socket(fileno=control_socket_fd)
    control_socket.sendall(READY_MESSAGE)
    buffer = b""
    pending_fds: List[int] = []
    while True:
        data, fds, _, _ = socket.recv_fds(control_socket, MAX_MESSAGE_SIZE, 2)
        if len(data) == 0:
            return
        buffer += data
        pending_fds.extend(fds)
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            request = json.loads(line)
            request_fds, pending_fds = pending_fds[:2], pending_fds[2:]
            assert len(request_fds) == 2, request_fds

            sys.stdout.flush()
            sys.stderr.flush()
            pid = os.fork()
            if pid == 0:
                _run_child(
                    control_socket=control_socket,
                    request=request,
                    fds=request_fds,
                )
            for fd_ in request_fds:
                os.close(fd_)
            control_socket.sendall(json.dumps({"pid": pid}).encode() + b"\n")


if __name__ == "__main__":
    # Running this file as a script puts tests/end2end/ first on sys.path,
    # where module names like "server" could hide other modules.
    if sys.path[0] == os.path.dirname(os.path.abspath(__file__)):
        sys.path.pop(0)
    serve(int(sys.argv[1]))
