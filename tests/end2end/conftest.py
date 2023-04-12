import os
import sys

import pytest
from seleniumbase.config import settings

from tests.end2end.sdoc_test_environment import SDocTestEnvironment

STRICTDOC_PATH = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(STRICTDOC_PATH), f"does not exist: {STRICTDOC_PATH}"
sys.path.append(STRICTDOC_PATH)

DOWNLOADED_FILES_PATH = os.path.join(STRICTDOC_PATH, "downloaded_files")

test_environment: SDocTestEnvironment = SDocTestEnvironment.create_default()


def pytest_addoption(parser):
    parser.addoption(
        "--strictdoc-long-timeouts", action="store_true", default=False
    )


def pytest_configure(config):
    long_timeouts = config.getoption("--strictdoc-long-timeouts")

    if long_timeouts:
        # Selenium timeout settings.
        settings.MINI_TIMEOUT = 5
        settings.SMALL_TIMEOUT = 10
        settings.LARGE_TIMEOUT = 15
        settings.EXTREME_TIMEOUT = 30

        test_environment.switch_to_long_timeouts()
    else:
        # Selenium timeout settings.
        settings.MINI_TIMEOUT = 2
        settings.SMALL_TIMEOUT = 7
        settings.LARGE_TIMEOUT = 10
        settings.EXTREME_TIMEOUT = 30


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
