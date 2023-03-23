import datetime
import os
import re

# FIXME: select has no poll() on Windows! Find a portable implementation.
import select
import shutil
import socket
import subprocess
from contextlib import closing
from threading import Thread
from time import sleep
from typing import Optional

import psutil
from psutil import NoSuchProcess

# Running selenium tests on GitHub Actions CI is considerably slower.
# Passing the flag via env because pytest makes it hard to introduce an extra
# command-line argument when it is not used as a test fixture.
from tests.end2end.conftest import test_environment


class ReadTimeout(Exception):
    def __init__(self, seconds_passed):
        assert isinstance(seconds_passed, float)
        self.seconds_passed = round(seconds_passed, 2)


class SDocTestServer:
    @staticmethod
    def create(input_path: str):
        if os.path.isdir(input_path):
            shutil.rmtree(input_path)
        os.mkdir(input_path)

        test_server = SDocTestServer(
            input_path=input_path,
            output_path=None,
        )
        return test_server

    def __init__(
        self,
        *,
        input_path: str,
        output_path: Optional[str] = None,
    ):
        is_parallel_execution = test_environment.is_parallel_execution

        assert os.path.isdir(input_path)
        self.path_to_tdoc_folder = input_path
        self.output_path: Optional[str] = output_path
        self.process = None
        self.server_port: int = (
            SDocTestServer._get_test_server_port()
            if is_parallel_execution
            else 5112
        )
        if not SDocTestServer.check_no_existing_connection(
            "127.0.0.1", self.server_port
        ):
            raise OSError(
                "TestSDocServer: Cannot start a server because there is another"
                f"server already running at the port: {self.server_port}."
            )

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
        args = [
            "python",
            "strictdoc/cli/main.py",
            "server",
            "--no-reload",
            "--port",
            str(self.server_port),
            self.path_to_tdoc_folder,
        ]
        if self.output_path is not None:
            args.extend(
                [
                    "--output-path",
                    self.output_path,
                ]
            )

        temp_file = open(  # pylint: disable=consider-using-with
            f"/tmp/strictdoc_server.{self.server_port}.out.log",
            "w",
            encoding="utf8",
        )

        process = subprocess.Popen(  # pylint: disable=consider-using-with
            args, stdout=temp_file.fileno(), stderr=subprocess.PIPE, shell=False
        )
        self.process = process

        # A non-blocking read on a subprocess.PIPE in Python
        # https://stackoverflow.com/a/59291466/598057
        os.set_blocking(  # pylint: disable=no-member
            process.stderr.fileno(), False
        )

        SDocTestServer.receive_expected_response(
            server_process=process,
            expectations=["INFO:     Application startup complete."],
        )
        SDocTestServer.continue_capturing_stderr(
            server_process=process, server_port=self.server_port
        )

        sleep(test_environment.warm_up_interval_seconds)
        print(  # noqa: T201
            f"TestSDocServer: "
            f"Server is up and running on port: {self.server_port}."
        )

    def close(self, *, exit_due_exception: Optional[Exception]) -> None:
        if self.process is None:
            return

        if exit_due_exception is not None:
            print(  # noqa: T201
                "\nTestSDocServer: exiting due to an exception.\n"
            )
            print(f"--- Exception ---\n {exit_due_exception}")  # noqa: T201
            last_lines_number = 10
            print(  # noqa: T201
                f"\n--- Captured Uvicorn stdout "
                f"(last {last_lines_number} lines) ---\n"
            )
            with open(
                f"/tmp/strictdoc_server.{self.server_port}.out.log",
                encoding="utf8",
            ) as out_temp_file:
                out_temp_file_lines = out_temp_file.readlines()[
                    -last_lines_number:
                ]
                print("".join(out_temp_file_lines))  # noqa: T201
            print("\n--- Captured Uvicorn stderr ---\n")  # noqa: T201

            with open(
                f"/tmp/strictdoc_server.{self.server_port}.err.log",
                encoding="utf8",
            ) as err_temp_file:
                print(err_temp_file.read())  # noqa: T201

        try:
            parent = psutil.Process(self.process.pid)
        except NoSuchProcess:
            print(  # noqa: T201
                "TestSDocServer: "
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
            "TestSDocServer: "
            "stopping server and worker processes: "
            f"{parent.pid} -> {child_processes_ids}"
        )
        self.process.kill()
        for process in child_processes:
            if process.is_running():
                process.kill()

    def get_host_and_port(self):
        return f"http://localhost:{self.server_port}"

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
    def check_no_existing_connection(host, port):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) == 0:
                return False
            return True

    @staticmethod
    def receive_expected_response(server_process, expectations):
        poll = select.poll()  # pylint: disable=no-member
        poll.register(
            server_process.stderr, select.POLLIN  # pylint: disable=no-member
        )  # pylint: disable=no-member
        received_input = []

        start_time = datetime.datetime.now()

        try:
            while len(expectations) > 0:
                check_time = datetime.datetime.now()
                diff_time = (check_time - start_time).total_seconds()
                if diff_time > float(test_environment.wait_timeout_seconds):
                    raise ReadTimeout(diff_time)

                # TODO: it could be that just polling for WAIT_TIMEOUT
                # is enough.
                if poll.poll(test_environment.poll_timeout_milliseconds):
                    line_bytes = server_process.stderr.readline()
                    while len(expectations) > 0 and line_bytes:
                        line_string = line_bytes.decode("utf-8")
                        current_expectation = expectations[0]
                        received_input.append(line_string)
                        if re.search(
                            current_expectation, f"{line_string.rstrip()}"
                        ):
                            expectations.pop(0)
                        line_bytes = server_process.stderr.readline()
        except ReadTimeout as timeout_exception:
            print(  # noqa: T201
                "\nFailed to get an expected response from the server within "
                f"{timeout_exception.seconds_passed} seconds."
            )
            received_lines = "".join(received_input)
            print(f"\n--- Received input ---\n\n{received_lines}")  # noqa: T201
            raise ReadTimeout(timeout_exception.seconds_passed) from None

    @staticmethod
    def enqueue_output(out, server_port: int):
        assert isinstance(server_port, int)
        # This solution also uses Queue but here it is not used.
        # https://stackoverflow.com/a/4896288/598057
        with open(
            f"/tmp/strictdoc_server.{server_port}.err.log", "wb"
        ) as temp_file:
            poll = select.poll()  # pylint: disable=no-member
            poll.register(out, select.POLLIN)  # pylint: disable=no-member

            while True:
                if poll.poll(1000):
                    line_bytes = out.readline()
                    while line_bytes:
                        temp_file.write(line_bytes)
                        line_bytes = out.readline()
                    temp_file.flush()

    @staticmethod
    def continue_capturing_stderr(server_process, server_port: int):
        thread = Thread(
            target=SDocTestServer.enqueue_output,
            args=(
                server_process.stderr,
                server_port,
            ),
        )
        thread.daemon = True  # thread dies with the program
        thread.start()
