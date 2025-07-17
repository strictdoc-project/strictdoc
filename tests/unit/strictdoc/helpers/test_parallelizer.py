import os
import signal
import sys
from time import sleep

import pytest

from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.parallelizer import MultiprocessingParallelizer


def child_process_that_multiplies_by_two(input_number):
    return input_number * 2


def child_process_that_fails(_):
    raise AssertionError("This child process always fails.")


def child_that_sigterms_itself_and_hangs(_):
    os.kill(os.getpid(), signal.SIGTERM)
    sleep(120)


def test_nominal_use_case():
    parallelizer = MultiprocessingParallelizer()

    input_items = [1, 2, 3]

    try:
        output_items = parallelizer.run_parallel(
            input_items, child_process_that_multiplies_by_two
        )

        assert list(output_items) == [2, 4, 6]
    finally:
        assert parallelizer.shutdown()


def test_if_child_process_fails_then_parallelizer_exits_with_non_zero():
    parallelizer = MultiprocessingParallelizer()

    input_items = ["FAKE_INPUT"]

    try:
        with pytest.raises(Exception) as exc_info:
            parallelizer.run_parallel(input_items, child_process_that_fails)

        assert exc_info.type is StrictDocException
        assert exc_info.value.args[0] == (
            "Parallelizer: One of the child processes has exited prematurely."
        )
    finally:
        assert not parallelizer.shutdown()


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Not tested on Windows"
)
def test_use_case_when_interrupted_with_sigterm():
    parallelizer = MultiprocessingParallelizer()

    input_items = ["FAKE_INPUT"]

    try:
        with pytest.raises(Exception) as exc_info:
            parallelizer.run_parallel(
                input_items, child_that_sigterms_itself_and_hangs
            )

        assert exc_info.type is StrictDocException
        assert exc_info.value.args[0] == (
            "Parallelizer: One of the child processes has exited prematurely."
        )
    finally:
        assert not parallelizer.shutdown()
