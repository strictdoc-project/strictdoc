import os
import sys

import pytest
from seleniumbase.config import settings

from strictdoc.helpers.shard import get_shard
from tests.end2end.sdoc_test_environment import SDocTestEnvironment

STRICTDOC_PATH = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(STRICTDOC_PATH), f"does not exist: {STRICTDOC_PATH}"
sys.path.append(STRICTDOC_PATH)

DOWNLOADED_FILES_PATH = os.path.join(STRICTDOC_PATH, "downloaded_files")

test_environment: SDocTestEnvironment = SDocTestEnvironment.create_default()


def pytest_collection_modifyitems(
    session, config, items  # pylint: disable=unused-argument
):
    """called after collection has been performed, may filter or re-order
    the items in-place."""

    shard = config.getoption("--strictdoc-shard")
    if shard is None:
        return

    shard_number, shard_total = map(int, shard.split("/"))
    shard_size = len(items) // shard_total

    left, right = get_shard(len(items), shard_total, shard_number)

    shard_items = items[left:right]
    items[:] = shard_items
    print(  # noqa: T201
        f"pytest: strictdoc: Shard argument provided: {shard}. "
        f"Shard size: {shard_size}. "
        f"Running tests in the range of: [{left}, {right})."
    )


def pytest_addoption(parser):
    parser.addoption(
        "--strictdoc-long-timeouts", action="store_true", default=False
    )
    parser.addoption(
        "--strictdoc-parallelize", action="store_true", default=False
    )
    parser.addoption("--strictdoc-shard", type=str, default=None)


def pytest_configure(config):
    long_timeouts = config.getoption("--strictdoc-long-timeouts")
    parallelize = config.getoption("--strictdoc-parallelize")

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

    if parallelize:
        test_environment.is_parallel_execution = True


class GlobalTestCounter:
    def __init__(self):
        self.total: int = 0
        self.total_run: int = 0
        self.total_failed: int = 0


test_counter = GlobalTestCounter()


# How to get the count of tests collected?
# https://stackoverflow.com/a/66515819/598057
def pytest_runtestloop(session):
    test_counter.total = len(session.items)


@pytest.fixture(autouse=True)
def run_around_tests():
    test_counter.total_run += 1

    print_line = f"-> Test {test_counter.total_run}/{test_counter.total}"
    if test_counter.total_failed > 0:
        print_line += f" ({test_counter.total_failed} failed)"

    print(print_line)  # noqa: T201

    yield


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
    """
    The actual wrapper that gets called before and after every test.
    https://stackoverflow.com/a/61526101/598057
    """

    outcome = yield

    result = outcome.get_result()

    if result.when == "call":
        if result.failed:
            test_counter.total_failed += 1
