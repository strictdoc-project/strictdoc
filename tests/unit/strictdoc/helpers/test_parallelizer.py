import os
import signal
import sys
from concurrent.futures.process import BrokenProcessPool
from time import sleep
from unittest import mock

import pytest

from strictdoc.helpers.exception import StrictDocChildProcessException
from strictdoc.helpers.parallelizer import (
    MultiprocessingParallelizer,
    NullParallelizer,
    _can_fork_safely,
    get_worker_context,
)


def child_process_that_multiplies_by_two(input_number):
    return input_number * 2


def child_process_that_fails(_):
    raise AssertionError("This child process always fails.")


def child_that_sigterms_itself_and_hangs(_):
    os.kill(os.getpid(), signal.SIGTERM)
    sleep(120)


def child_process_that_reads_the_worker_context(_):
    return get_worker_context()


def test_nominal_use_case():
    parallelizer = MultiprocessingParallelizer()

    input_items = [1, 2, 3]

    try:
        output_items = parallelizer.run_parallel(
            input_items, child_process_that_multiplies_by_two
        )

        assert list(output_items) == [2, 4, 6]
    finally:
        parallelizer.shutdown()


def test_if_child_process_fails_then_parallelizer_exits_with_non_zero():
    parallelizer = MultiprocessingParallelizer()

    input_items = ["FAKE_INPUT"]

    try:
        with pytest.raises(Exception) as exc_info:
            parallelizer.run_parallel(input_items, child_process_that_fails)

        assert exc_info.type is StrictDocChildProcessException
        assert exc_info.value.args[0].exception.args[0] == (
            "This child process always fails."
        )
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_sends_context_once_per_worker():
    parallelizer = MultiprocessingParallelizer()

    try:
        output_items = parallelizer.run_parallel_with_context(
            [1, 2, 3],
            child_process_that_reads_the_worker_context,
            "shared-context",
        )

        assert list(output_items) == ["shared-context"] * 3
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_can_be_called_again_with_a_new_context():
    parallelizer = MultiprocessingParallelizer()

    try:
        first_result = parallelizer.run_parallel_with_context(
            [1], child_process_that_reads_the_worker_context, "first"
        )
        second_result = parallelizer.run_parallel_with_context(
            [1], child_process_that_reads_the_worker_context, "second"
        )

        assert list(first_result) == ["first"]
        assert list(second_result) == ["second"]
    finally:
        parallelizer.shutdown()


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="fork is not available on Windows"
)
def test_can_fork_safely_true_when_single_threaded():
    with mock.patch(
        "strictdoc.helpers.parallelizer.threading.active_count",
        return_value=1,
    ):
        assert _can_fork_safely() is True


def test_can_fork_safely_false_when_not_single_threaded():
    # A live background thread makes forking unsafe: a lock it holds could
    # be left permanently locked (and never released) in the forked child,
    # which only inherits a frozen snapshot of the parent's memory, not
    # the thread that was about to release that lock.
    with mock.patch(
        "strictdoc.helpers.parallelizer.threading.active_count",
        return_value=2,
    ):
        assert _can_fork_safely() is False


def test_can_fork_safely_false_when_fork_unavailable():
    with mock.patch(
        "strictdoc.helpers.parallelizer.threading.active_count",
        return_value=1,
    ), mock.patch(
        "strictdoc.helpers.parallelizer.multiprocessing.get_all_start_methods",
        return_value=["spawn"],
    ):
        assert _can_fork_safely() is False


def test_run_parallel_with_context_falls_back_when_not_safe_to_fork():
    parallelizer = MultiprocessingParallelizer()

    try:
        with mock.patch(
            "strictdoc.helpers.parallelizer._can_fork_safely",
            return_value=False,
        ):
            output_items = parallelizer.run_parallel_with_context(
                [1, 2, 3],
                child_process_that_reads_the_worker_context,
                "fallback-context",
            )

        assert list(output_items) == ["fallback-context"] * 3
        assert parallelizer.executor._mp_context.get_start_method() != "fork"
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_runs_in_process_when_not_safe_to_fork_and_many_tasks():
    # Without fork+COW (Windows, always - or a caller that isn't
    # single-threaded), sending a large `context` to every worker via the
    # pool initializer doesn't scale (see run_parallel_with_context()'s
    # comments for the measurements). Above the task-count threshold used
    # as a size proxy, this must skip multiprocessing for the call
    # entirely rather than duplicate `context` into a whole pool of
    # workers - the same protection html_generator.py's now-removed
    # document-count cutoff used to provide unconditionally.
    parallelizer = MultiprocessingParallelizer()

    try:
        many_items = list(range(30))

        with mock.patch(
            "strictdoc.helpers.parallelizer._can_fork_safely",
            return_value=False,
        ):
            output_items = parallelizer.run_parallel_with_context(
                many_items,
                child_process_that_reads_the_worker_context,
                "large-fallback-context",
            )

        assert output_items == ["large-fallback-context"] * len(many_items)
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_null_parallelizer():
    parallelizer = NullParallelizer()

    output_items = parallelizer.run_parallel_with_context(
        [1, 2], child_process_that_reads_the_worker_context, "null-context"
    )

    assert output_items == ["null-context", "null-context"]


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

        assert exc_info.type is BrokenProcessPool
        assert exc_info.value.args[0] == (
            "A process in the process pool was terminated abruptly while the future was running or pending."
        )
    finally:
        parallelizer.shutdown()
