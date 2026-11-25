import os
import signal
import sys
from concurrent.futures.process import BrokenProcessPool
from time import sleep

import pytest

from strictdoc.helpers.exception import StrictDocChildProcessException
from strictdoc.helpers.parallelizer import (
    MIN_TASKS_FOR_PROCESS_POOL,
    MultiprocessingParallelizer,
    NullParallelizer,
    get_worker_context,
)

# The smallest calls that still run in worker processes, and the largest calls
# that run in the calling process.
POOL_SIZED_ITEMS = list(range(1, MIN_TASKS_FOR_PROCESS_POOL + 1))
IN_PROCESS_SIZED_ITEMS = list(range(1, MIN_TASKS_FOR_PROCESS_POOL))

# MultiprocessingParallelizer(dynamic=False) always forks (see its
# docstring), which is correct for the real, genuinely single-threaded CLI
# export process it's built for. Under pytest, though, the process is not
# single-threaded: pytest-rerunfailures starts its own background thread
# (ServerStatusDB.run_server) unconditionally, just by being installed, with
# no relation to these tests or to --reruns being passed. That's what makes
# fork() below emit CPython's "process is multi-threaded" DeprecationWarning
# here - not anything about this module's code.
pytestmark = pytest.mark.filterwarnings(
    "ignore::DeprecationWarning:multiprocessing.popen_fork"
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


def child_process_that_returns_its_process_id(_):
    return os.getpid()


class ExceptionWithKeywordOnlyInit(Exception):
    """
    Mirrors StrictDocSemanticError's shape: a keyword-only __init__ that
    forwards positional args to Exception.__init__(), which is exactly what
    breaks Exception's default __reduce__ (`type(exc)(*exc.args)`) when the
    exception has to be pickled back from a worker process.
    """

    def __init__(self, *, title):
        super().__init__(title)
        self.title = title


def child_process_that_raises_an_unpicklable_exception(_):
    raise ExceptionWithKeywordOnlyInit(title="This exception is not picklable.")


def test_nominal_use_case():
    parallelizer = MultiprocessingParallelizer()

    try:
        output_items = parallelizer.run_parallel(
            POOL_SIZED_ITEMS, child_process_that_multiplies_by_two
        )

        assert list(output_items) == [item_ * 2 for item_ in POOL_SIZED_ITEMS]
    finally:
        parallelizer.shutdown()


def test_if_child_process_fails_then_parallelizer_exits_with_non_zero():
    parallelizer = MultiprocessingParallelizer()

    try:
        with pytest.raises(Exception) as exc_info:
            parallelizer.run_parallel(
                POOL_SIZED_ITEMS, child_process_that_fails
            )

        assert exc_info.type is StrictDocChildProcessException
        assert exc_info.value.args[0].exception_message == (
            "This child process always fails."
        )
    finally:
        parallelizer.shutdown()


def test_if_child_process_raises_an_exception_with_a_non_standard_init_it_still_propagates():
    """
    Regression test: a worker exception whose __init__ doesn't accept
    Exception's default __reduce__ round-trip (`type(exc)(*exc.args)`) used
    to make the wrapping StrictDocChildProcessException itself unpicklable,
    turning a normal, reportable error into an opaque BrokenProcessPool
    crash instead of propagating the real error message.
    """
    parallelizer = MultiprocessingParallelizer()

    try:
        with pytest.raises(Exception) as exc_info:
            parallelizer.run_parallel(
                POOL_SIZED_ITEMS,
                child_process_that_raises_an_unpicklable_exception,
            )

        assert exc_info.type is StrictDocChildProcessException
        assert exc_info.value.args[0].exception_message == (
            "This exception is not picklable."
        )
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_sends_context_once_per_worker():
    parallelizer = MultiprocessingParallelizer()

    try:
        output_items = parallelizer.run_parallel_with_context(
            POOL_SIZED_ITEMS,
            child_process_that_reads_the_worker_context,
            "shared-context",
        )

        assert list(output_items) == ["shared-context"] * len(POOL_SIZED_ITEMS)
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_can_be_called_again_with_a_new_context():
    parallelizer = MultiprocessingParallelizer()

    try:
        first_result = parallelizer.run_parallel_with_context(
            POOL_SIZED_ITEMS,
            child_process_that_reads_the_worker_context,
            "first",
        )
        second_result = parallelizer.run_parallel_with_context(
            POOL_SIZED_ITEMS,
            child_process_that_reads_the_worker_context,
            "second",
        )

        assert list(first_result) == ["first"] * len(POOL_SIZED_ITEMS)
        assert list(second_result) == ["second"] * len(POOL_SIZED_ITEMS)
    finally:
        parallelizer.shutdown()


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="fork is not available on Windows"
)
def test_non_dynamic_parallelizer_uses_fork():
    parallelizer = MultiprocessingParallelizer(dynamic=False)
    try:
        assert parallelizer.mp_context.get_start_method() == "fork"
    finally:
        parallelizer.shutdown()


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="fork is not available on Windows"
)
def test_dynamic_parallelizer_uses_forkserver_not_fork():
    parallelizer = MultiprocessingParallelizer(dynamic=True)
    try:
        assert parallelizer.mp_context.get_start_method() != "fork"
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_falls_back_when_dynamic():
    parallelizer = MultiprocessingParallelizer(dynamic=True)

    try:
        output_items = parallelizer.run_parallel_with_context(
            POOL_SIZED_ITEMS,
            child_process_that_reads_the_worker_context,
            "fallback-context",
        )

        assert list(output_items) == ["fallback-context"] * len(
            POOL_SIZED_ITEMS
        )
        assert parallelizer.executor._mp_context.get_start_method() != "fork"
    finally:
        parallelizer.shutdown()


def test_run_parallel_with_context_runs_in_process_when_dynamic_and_many_tasks():
    # A dynamic Parallelizer never uses "fork" (see __init__), so a large
    # `context` sent to every worker via the pool initializer doesn't scale
    # (see run_parallel_with_context()'s comments for the measurements).
    # Above the task-count threshold used as a size proxy, this must skip
    # multiprocessing for the call entirely rather than duplicate `context`
    # into a whole pool of workers - the same protection html_generator.py's
    # now-removed document-count cutoff used to provide unconditionally.
    parallelizer = MultiprocessingParallelizer(dynamic=True)

    try:
        many_items = list(range(30))

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

    try:
        with pytest.raises(Exception) as exc_info:
            parallelizer.run_parallel(
                POOL_SIZED_ITEMS, child_that_sigterms_itself_and_hangs
            )

        assert exc_info.type is BrokenProcessPool
        assert exc_info.value.args[0] == (
            "A process in the process pool was terminated abruptly while the future was running or pending."
        )
    finally:
        parallelizer.shutdown()


def test_run_parallel_uses_worker_processes_from_the_threshold():
    parallelizer = MultiprocessingParallelizer()

    try:
        process_ids = parallelizer.run_parallel(
            POOL_SIZED_ITEMS, child_process_that_returns_its_process_id
        )

        assert os.getpid() not in process_ids
    finally:
        parallelizer.shutdown()


def test_run_parallel_runs_in_process_below_the_threshold():
    parallelizer = MultiprocessingParallelizer()

    try:
        completed_indexes = []
        process_ids = parallelizer.run_parallel(
            IN_PROCESS_SIZED_ITEMS,
            child_process_that_returns_its_process_id,
            lambda index_, _: completed_indexes.append(index_),
        )

        assert process_ids == [os.getpid()] * len(IN_PROCESS_SIZED_ITEMS)
        assert completed_indexes == list(range(len(IN_PROCESS_SIZED_ITEMS)))
    finally:
        parallelizer.shutdown()


def test_run_parallel_below_the_threshold_raises_the_child_process_exception():
    """
    A failed task in the calling process raises the same exception as a
    failed task in a worker process.
    """
    parallelizer = MultiprocessingParallelizer()

    try:
        with pytest.raises(StrictDocChildProcessException) as exc_info:
            parallelizer.run_parallel(
                IN_PROCESS_SIZED_ITEMS, child_process_that_fails
            )

        assert exc_info.value.args[0].exception_message == (
            "This child process always fails."
        )
    finally:
        parallelizer.shutdown()


@pytest.mark.parametrize("dynamic", [False, True])
def test_run_parallel_with_context_runs_in_process_below_the_threshold(
    dynamic,
):
    parallelizer = MultiprocessingParallelizer(dynamic=dynamic)

    try:
        executor_before = parallelizer.executor

        output_items = parallelizer.run_parallel_with_context(
            IN_PROCESS_SIZED_ITEMS,
            child_process_that_reads_the_worker_context,
            "in-process-context",
        )
        process_ids = parallelizer.run_parallel_with_context(
            IN_PROCESS_SIZED_ITEMS,
            child_process_that_returns_its_process_id,
            "in-process-context",
        )

        assert output_items == ["in-process-context"] * len(
            IN_PROCESS_SIZED_ITEMS
        )
        assert process_ids == [os.getpid()] * len(IN_PROCESS_SIZED_ITEMS)
        # The in-process path neither shuts down nor rebuilds the pool.
        assert parallelizer.executor is executor_before
    finally:
        parallelizer.shutdown()
