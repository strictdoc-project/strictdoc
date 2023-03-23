import os
import sys

import pytest
from seleniumbase.config import settings

from tests.end2end.sdoc_test_environment import SDocTestEnvironment

STRICTDOC_PATH = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(STRICTDOC_PATH), f"does not exist: {STRICTDOC_PATH}"
sys.path.append(STRICTDOC_PATH)

DOWNLOADED_FILES_PATH = os.path.join(STRICTDOC_PATH, "downloaded_files")


# Running Selenium tests on GitHub Actions CI is considerably slower.
# Passing the flag via env because pytest makes it hard to introduce an extra
# command-line argument when it is not used as a test fixture.
if os.getenv("STRICTDOC_LONGER_TIMEOUTS") is not None:
    WAIT_TIMEOUT = 30
    POLL_TIMEOUT = 1
    WARMUP_INTERVAL = 3
    DOWNLOAD_FILE_TIMEOUT = 5
    SERVER_TERM_TIMEOUT = 5

    # Selenium timeout settings
    settings.MINI_TIMEOUT = 5
    settings.SMALL_TIMEOUT = 10
    settings.LARGE_TIMEOUT = 15
    settings.EXTREME_TIMEOUT = 30
else:
    WAIT_TIMEOUT = 5
    POLL_TIMEOUT = 0.1
    WARMUP_INTERVAL = 0
    DOWNLOAD_FILE_TIMEOUT = 2
    SERVER_TERM_TIMEOUT = 1

    # Selenium timeout settings
    settings.MINI_TIMEOUT = 2
    settings.SMALL_TIMEOUT = 7
    settings.LARGE_TIMEOUT = 10
    settings.EXTREME_TIMEOUT = 30

test_environment = SDocTestEnvironment(
    is_parallel_execution="STRICTDOC_PARALLELIZE" in os.environ,
    wait_timeout_seconds=WAIT_TIMEOUT,
    poll_timeout_seconds=POLL_TIMEOUT,
    warm_up_interval_seconds=WARMUP_INTERVAL,
    download_file_timeout_seconds=DOWNLOAD_FILE_TIMEOUT,
    server_term_timeout_seconds=SERVER_TERM_TIMEOUT,
)

TESTS_TOTAL = 0


# How to get the count of tests collected?
# https://stackoverflow.com/a/66515819/598057
def pytest_runtestloop(session):
    global TESTS_TOTAL  # pylint: disable=global-statement
    TESTS_TOTAL = len(session.items)


TEST_COUNTER = 0


@pytest.fixture(autouse=True)
def run_around_tests():
    global TEST_COUNTER  # pylint: disable=global-statement
    TEST_COUNTER += 1
    print(f"-> Test {TEST_COUNTER}/{TESTS_TOTAL}")  # noqa: T201
    yield
