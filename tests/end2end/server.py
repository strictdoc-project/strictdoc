import datetime
import os
import re

# FIXME: select has no poll() on Windows. Find a portable implementation.
import select
import shutil
import subprocess
import sys
from threading import Thread
from time import sleep

import psutil

# Running selenium tests on GitHub Actions CI is considerably slower.
# Passing the flag via env because pytest makes it hard to introduce an extra
# command-line argument when it is not used as a test fixture.
if os.getenv("STRICTDOC_LONGER_TIMEOUTS") is not None:
    WAIT_TIMEOUT = 30
    POLL_TIMEOUT = 10000
    WARMUP_INTERVAL = 3
    # When Selenium clicks on a link that downloads a file, it takes some time
    # until the file actually appears on the file system.
    DOWNLOAD_FILE_TIMEOUT = 4
else:
    WAIT_TIMEOUT = 5
    POLL_TIMEOUT = 2000
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

        # _ = GitClient(path_to_git_root=path_to_sandbox, initialize=True)

        test_server = SDocTestServer(
            input_path=path_to_sandbox,
            output_path=None,
        )
        return test_server

    def __init__(self, input_path, output_path):
        assert os.path.isdir(input_path)
        self.path_to_tdoc_folder = input_path
        self.path_to_sandbox = output_path
        self.process = None

    def __del__(self):
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
            process.kill()

    def run(self):
        args = [
            "python",
            "strictdoc/cli/main.py",
            "server",
            "--no-reload",
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
            "/tmp/sdoctest.out.log", "w", encoding="utf8"
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
        SDocTestServer.continue_capturing_stderr(server_process=process)

        sleep(WARMUP_INTERVAL)
        print("TestSDocServer: Server is up and running.")

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
    def enqueue_output(out):
        # This solution also uses Queue but here it is not used.
        # https://stackoverflow.com/a/4896288/598057
        with open("/tmp/sdoctest.err.log", "wb") as temp_file:
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
    def continue_capturing_stderr(server_process):
        thread = Thread(
            target=SDocTestServer.enqueue_output, args=(server_process.stderr,)
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
