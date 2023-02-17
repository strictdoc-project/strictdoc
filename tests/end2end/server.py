import datetime
import os
import re

# FIXME: select has no poll() on Windows. Find a portable implementation.
import select
import shutil
import socket
import subprocess
import sys
from contextlib import closing
from threading import Thread
from time import sleep
from typing import Optional

import psutil

# Running selenium tests on GitHub Actions CI is considerably slower.
# Passing the flag via env because pytest makes it hard to introduce an extra
# command-line argument when it is not used as a test fixture.
from tests.end2end.conftest import test_environment

if os.getenv("STRICTDOC_LONGER_TIMEOUTS") is not None:
    WAIT_TIMEOUT = 30
    POLL_TIMEOUT = 10000
    WARMUP_INTERVAL = 3
    # When Selenium clicks on a link that downloads a file, it takes some time
    # until the file actually appears on the file system.
    DOWNLOAD_FILE_TIMEOUT = 5
else:
    WAIT_TIMEOUT = 5  # Seconds
    POLL_TIMEOUT = 2000  # Milliseconds
    WARMUP_INTERVAL = 0
    DOWNLOAD_FILE_TIMEOUT = 2


class ReadTimeout(Exception):
    pass


class SDocTestServer:
    @staticmethod
    def create(path_to_sandbox: str):
        if os.path.isdir(path_to_sandbox):
            shutil.rmtree(path_to_sandbox)
        os.mkdir(path_to_sandbox)

        test_server = SDocTestServer(
            input_path=path_to_sandbox,
            output_path=None,
            is_parallel_execution=test_environment.is_parallel_execution,
        )
        return test_server

    def __init__(
        self,
        *,
        input_path: str,
        output_path: Optional[str] = None,
        is_parallel_execution: bool = False,
    ):
        assert os.path.isdir(input_path)
        self.path_to_tdoc_folder = input_path
        self.path_to_sandbox: Optional[str] = output_path
        self.process = None
        self.server_port: int = (
            SDocTestServer._get_test_server_port()
            if is_parallel_execution
            else 5112
        )
        if not SDocTestServer.check_no_existing_connection(
            "127.0.0.1", self.server_port
        ):
            raise EnvironmentError(
                "TestSDocServer: Cannot start a server because there is another"
                f"server already running at the port: {self.server_port}."
            )

    def __del__(self):
        self.close()

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
        if self.path_to_sandbox is not None:
            args.extend(
                [
                    "--output-path",
                    self.path_to_sandbox,
                ]
            )

        temp_file = open(  # pylint: disable=consider-using-with
            f"/tmp/strictdoc_server.{self.server_port}.out.log",
            "a",
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

        sleep(WARMUP_INTERVAL)
        print(
            f"TestSDocServer: "
            f"Server is up and running on port: {self.server_port}."
        )

    def close(self):
        if self.process is None:
            return
        parent = psutil.Process(self.process.pid)
        if not parent.is_running():
            return
        child_processes = parent.children(recursive=True)
        child_processes_ids = list(
            map(lambda p: p.pid, parent.children(recursive=True))
        )
        print(
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
                if (check_time - start_time).total_seconds() > WAIT_TIMEOUT:
                    raise ReadTimeout()

                if poll.poll(POLL_TIMEOUT):
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
                else:
                    raise ReadTimeout()
        except ReadTimeout:
            print(
                "---------------------------------------------------------------------"  # noqa: E501
            )
            print("Failed to get an expected response from the server.")
            received_lines = "".join(received_input)
            print(f"Received input:\n{received_lines}")
            sys.exit(1)

    @staticmethod
    def enqueue_output(out, server_port: int):
        assert isinstance(server_port, int)
        # This solution also uses Queue but here it is not used.
        # https://stackoverflow.com/a/4896288/598057
        with open(
            f"/tmp/strictdoc_server.{server_port}.err.log", "ab"
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

        # # read line without blocking
        # try:
        #     line = q.get_nowait()  # or q.get(timeout=.1)
        # except Empty:
        #     print('no output yet')
        # else:
        #
