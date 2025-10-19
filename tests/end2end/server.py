"""
This implementation is loosely based on:
A non-blocking read on a subprocess.PIPE in Python,
https://stackoverflow.com/a/4896288/598057
TODO: Consider switching from subprocess to asyncio for starting a server...
https://stackoverflow.com/a/68564737/598057

@relation(SDOC-SRS-46, scope=file)
"""

import datetime
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from contextlib import ExitStack, closing
from queue import Empty, Queue
from threading import Event, Thread
from time import sleep
from typing import Dict, List, Optional, Tuple

import psutil
from psutil import NoSuchProcess

from strictdoc import environment
from strictdoc.helpers.file_system import get_portable_temp_dir
from tests.end2end.conftest import test_environment


class ReadTimeout(Exception):
    def __init__(self, seconds_passed):
        assert isinstance(seconds_passed, float)
        self.seconds_passed = round(seconds_passed, 2)


class ServerStderrReadThread(Thread):
    def __init__(self, server: "SDocTestServer", process_stderr):
        super().__init__(daemon=True)
        self.server: SDocTestServer = server
        self.process_stderr = process_stderr

    def run(self):
        # Iteration through the process_stderr.readline is blocking.
        for line in iter(self.process_stderr.readline, b""):
            self.server.stderr_queue.put(line)


class TestStderrLogThread(Thread):
    def __init__(self, server: "SDocTestServer"):
        super().__init__()
        self.server: SDocTestServer = server
        self.stderr_queue = server.stderr_queue
        self.stop_event = Event()

    def run(self):
        stderr_log_file = self.server.log_file_err
        while not self.stop_event.is_set():
            try:
                line_bytes = self.stderr_queue.get(
                    timeout=test_environment.poll_timeout_seconds
                )
            except Empty:
                continue
            stderr_log_file.write(line_bytes)
            stderr_log_file.flush()


class SDocTestServer:
    @staticmethod
    def create(input_path: str):
        if os.path.isdir(input_path):
            shutil.rmtree(input_path)
        os.mkdir(input_path)

        test_server = SDocTestServer(
            input_path=input_path,
            output_path=None,
            expectations=None,
        )
        return test_server

    def __init__(
        self,
        *,
        input_path: str,
        output_path: Optional[str] = None,
        config_path: Optional[str] = None,
        port: Optional[int] = None,
        expectations: Optional[List] = None,
        cwd: Optional[str] = None,
    ):
        is_parallel_execution = test_environment.is_parallel_execution

        assert os.path.isdir(input_path)
        if config_path is not None:
            assert os.path.exists(config_path), config_path
        if cwd is not None:
            assert os.path.isdir(cwd), cwd

        self.path_to_tdoc_folder = input_path
        self.output_path: Optional[str] = output_path
        self.config_path: Optional[str] = config_path
        self.server_port: int = (
            SDocTestServer._get_test_server_port()
            if is_parallel_execution
            else port
            if port is not None
            else 5112
        )
        if SDocTestServer.check_existing_connection(
            "127.0.0.1", self.server_port
        ):
            raise OSError(
                "SDocTestServer: Cannot start a server because there is another"
                f"server already running at the port: {self.server_port}."
            )
        path_to_tmp_dir = get_portable_temp_dir()
        self.path_to_out_log = os.path.join(
            path_to_tmp_dir, f"strictdoc_server.{self.server_port}.out.log"
        )
        self.path_to_err_log = os.path.join(
            path_to_tmp_dir, f"strictdoc_server.{self.server_port}.err.log"
        )

        self.expectations = (
            expectations
            if expectations is not None
            else ["INFO:     Application startup complete."]
        )

        self.cwd: str = cwd if cwd is not None else input_path
        self.path_to_strictdoc: str = os.path.join(
            environment.path_to_strictdoc, "strictdoc/cli/main.py"
        )

        # All of these below become initialized/used starting from run()
        self.process = None
        self.log_file_out = None
        self.log_file_err = None
        self.stderr_queue = Queue()
        self.exit_stack = ExitStack()
        self.server_stderr_capture_thread: Optional[ServerStderrReadThread] = (
            None
        )
        self.test_stderr_log_thread: Optional[TestStderrLogThread] = None

    def __enter__(self):
        self.run()
        return self

    def __exit__(
        self, type__, reason_exception: Optional[Exception], traceback
    ):
        self.close(exit_due_exception=reason_exception)
        if reason_exception is not None:
            raise reason_exception from None

    def run(self):
        strictdoc_args, strictdoc_env = self._get_strictdoc_command()
        self.log_file_out = open(  # pylint: disable=consider-using-with
            self.path_to_out_log, "wb"
        )
        self.log_file_err = open(  # pylint: disable=consider-using-with
            self.path_to_err_log, "wb"
        )
        self.exit_stack.enter_context(self.log_file_out)
        self.exit_stack.enter_context(self.log_file_err)

        process = subprocess.Popen(  # pylint: disable=consider-using-with
            strictdoc_args,
            stdout=self.log_file_out.fileno(),
            stderr=subprocess.PIPE,
            shell=False,
            cwd=self.cwd,
            env=strictdoc_env,
        )
        self.process = process

        self.server_stderr_capture_thread = ServerStderrReadThread(
            server=self,
            process_stderr=process.stderr,
        )
        self.server_stderr_capture_thread.start()

        # Capture first startup lines.
        self.capture_expected_server_stderr_response(
            expectations=self.expectations,
        )

        # Continue writing captured stderr output to the log file.
        self.test_stderr_log_thread = TestStderrLogThread(server=self)
        self.test_stderr_log_thread.start()

        sleep(test_environment.warm_up_interval_seconds)
        print(  # noqa: T201
            f"SDocTestServer: "
            f"Server is up and running on port: {self.server_port}."
        )

    def close(self, *, exit_due_exception: Optional[Exception]) -> None:
        if self.process is not None:
            try:
                parent = psutil.Process(self.process.pid)
            except NoSuchProcess:
                print(  # noqa: T201
                    "SDocTestServer: "
                    "no need to stop the server process because it is not running: "
                    f"{self.process.pid}.",
                    flush=True,
                )
                return

            if not parent.is_running():
                return

            child_processes = parent.children(recursive=True)
            child_processes_ids = list(
                map(lambda p: p.pid, parent.children(recursive=True))
            )
            print(  # noqa: T201
                "SDocTestServer: "
                "stopping server and worker processes: "
                f"{parent.pid} -> {child_processes_ids}"
            )

            #
            # Sending SIGTERM to StrictDoc's FastAPI.
            # When running with code coverage, the FastAPI server subscribes to
            # SIGTERM in order to save the current code coverage when the
            # process is being terminated.
            #
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=1)
            self.process.terminate()

            for process_ in child_processes:
                if process_.is_running():
                    process_.send_signal(signal.SIGTERM)

            #
            # Wait for all processes to exit gracefully.
            #
            start_time = time.monotonic()
            timeout = 5
            while True:
                alive = [p for p in child_processes if p.is_running()]
                if len(alive) == 0:
                    print(  # noqa: T201
                        "SDocTestServer: "
                        "server and worker processes were terminated "
                        "successfully: "
                        f"{parent.pid} -> {child_processes_ids}"
                    )
                    break

                if (time.monotonic() - start_time) > timeout:
                    print(  # noqa: T201
                        "SDocTestServer: "
                        "Timeout reached. Some StrictDoc server child processes "
                        "did not terminate: "
                        f"{alive}."
                    )
                    for process in child_processes:
                        try:
                            if process.is_running():
                                process.kill()
                        except psutil.NoSuchProcess:
                            continue
                    break

                time.sleep(0.1)

            start_time = datetime.datetime.now()
            while True:
                if not SDocTestServer.check_existing_connection(
                    "127.0.0.1", self.server_port
                ):
                    break

                check_time = datetime.datetime.now()
                diff_time = (check_time - start_time).total_seconds()
                if diff_time > float(test_environment.server_term_timeout):
                    raise OSError(
                        "SDocTestServer: Sent SIGTERM to a server but could not"
                        "wait until the server port is released: "
                        f"{self.server_port}."
                    )
                sleep(0.1)

        assert isinstance(
            self.server_stderr_capture_thread, ServerStderrReadThread
        ), self.server_stderr_capture_thread

        if self.test_stderr_log_thread is not None:
            self.test_stderr_log_thread.stop_event.set()
            self.test_stderr_log_thread.join()

        if self.server_stderr_capture_thread is not None:
            self.server_stderr_capture_thread.join()

        self.exit_stack.close()

        if exit_due_exception is not None:
            print(  # noqa: T201
                "\nSDocTestServer: exiting due to an exception.\n"
            )
            print(f"--- Exception ---\n {exit_due_exception}")  # noqa: T201
            last_lines_number = 25
            print(  # noqa: T201
                f"\n--- Captured Uvicorn stdout "
                f"(last {last_lines_number} lines) ---\n"
            )
            with open(self.path_to_out_log, encoding="utf8") as out_temp_file:
                out_temp_file_lines = out_temp_file.readlines()[
                    -last_lines_number:
                ]
                print("".join(out_temp_file_lines))  # noqa: T201
            print("\n--- Captured Uvicorn stderr ---\n")  # noqa: T201

            with open(self.path_to_err_log, encoding="utf8") as err_temp_file:
                print(err_temp_file.read())  # noqa: T201

    def get_host_and_port(self):
        return f"http://localhost:{self.server_port}"

    def _get_strictdoc_command(self) -> Tuple[List[str], Dict[str, str]]:
        # It is important that the current environment is passed along with the
        # server command, otherwise the Python packages will not be discovered.
        strictdoc_env: Dict[str, str] = dict(os.environ)

        should_collect_coverage = test_environment.coverage
        strictdoc_args: List[str] = [sys.executable]
        if should_collect_coverage:
            path_to_coverage_rc = os.path.join(
                environment.path_to_strictdoc, ".coveragerc.end2end"
            )
            path_to_coverage = os.path.join(
                environment.path_to_strictdoc,
                "build/coverage/end2end_strictdoc",
                ".coverage",
            )
            strictdoc_args.extend(
                [
                    "-m",
                    "coverage",
                    "run",
                    f"--rcfile={path_to_coverage_rc}",
                    f"--data-file={path_to_coverage}",
                ]
            )
            strictdoc_env.update(
                {
                    # This is not used by coverage itself but StrictDoc uses it as
                    # a condition to activate the exit hooks for preserving coverage.
                    # See strictdoc.helpers.coverage.register_code_coverage_hook.
                    "COVERAGE_PROCESS_START": path_to_coverage_rc,
                }
            )

        strictdoc_args.extend(
            [
                self.path_to_strictdoc,
                "server",
                "--no-reload",
                "--port",
                str(self.server_port),
                self.path_to_tdoc_folder,
            ]
        )

        if self.config_path:
            strictdoc_args.extend(["--config", self.config_path])
        if self.output_path is not None:
            strictdoc_args.extend(
                [
                    "--output-path",
                    self.output_path,
                ]
            )

        return strictdoc_args, strictdoc_env

    @staticmethod
    def _get_test_server_port() -> int:
        # This is to avoid collisions between test processes running in
        # parallel.
        base_server_test_port = 5113
        this_process_pid = os.getpid()
        this_process_pid_hundreds = this_process_pid % 100
        server_port = base_server_test_port + this_process_pid_hundreds
        return server_port

    @staticmethod
    def check_existing_connection(host, port):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) == 0:
                return True
            return False

    def capture_expected_server_stderr_response(self, expectations):
        received_input = []

        start_time = datetime.datetime.now()

        try:
            while len(expectations) > 0:
                check_time = datetime.datetime.now()
                diff_time = (check_time - start_time).total_seconds()
                if diff_time > float(test_environment.wait_timeout_seconds):
                    raise ReadTimeout(diff_time)

                try:
                    line_bytes = self.stderr_queue.get(
                        timeout=test_environment.poll_timeout_seconds
                    )
                    assert isinstance(line_bytes, bytes), line_bytes
                    self.log_file_err.write(line_bytes)

                    if len(expectations) > 0:
                        line_string = line_bytes.decode("utf-8")
                        current_expectation = expectations[0]
                        received_input.append(line_string)
                        if line_string.rstrip() in current_expectation:
                            expectations.pop(0)
                except Empty:
                    pass
        except ReadTimeout as timeout_exception:
            print(  # noqa: T201
                "\nFailed to get an expected response from the server within "
                f"{timeout_exception.seconds_passed} seconds."
            )
            received_lines = "".join(received_input)
            print(f"\n--- Received input ---\n\n{received_lines}")  # noqa: T201
            raise ReadTimeout(timeout_exception.seconds_passed) from None
