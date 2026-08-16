"""
Run StrictDoc child tasks as separate processes.

@relation(SDOC-SRS-1, scope=file)
"""

import multiprocessing
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Callable, Iterable, List, Optional, Tuple

from strictdoc import environment
from strictdoc.helpers.exception import (
    ExceptionInfo,
    StrictDocChildProcessException,
)

MultiprocessingLambdaType = Callable[[Any], Any]

# Where run_parallel_with_context() cannot use the fork+copy-on-write fast
# path (Windows, always - or a dynamic MultiprocessingParallelizer, which
# never uses "fork" - see MultiprocessingParallelizer.__init__()), this caps
# how many tasks it will still dispatch via the pool-initializer mechanism
# before falling back to running in-process instead. Task count is only a
# rough proxy for the size of the shared `context` object actually being
# duplicated per worker, but this is the same document-count cutoff (25)
# html_generator.py used to apply unconditionally before the fork+COW path
# existed - see run_parallel_with_context() below for the measurements
# behind it.
_LARGE_CONTEXT_FALLBACK_THRESHOLD = 25

# Set once per worker process by _init_worker_context() (either via a pool
# initializer under multiprocessing, or directly in-process under
# NullParallelizer). run_parallel_with_context() exists so that a large,
# shared, read-only value (e.g. a whole traceability index) is sent to each
# worker process exactly once, instead of being pickled fresh into every
# submitted task's closure/arguments.
#
# A single-item box, rather than a rebound module-level name, so that
# _init_worker_context() can set it without a `global` statement.
_worker_context_box: List[Any] = [None]


def _init_worker_context(context: Any) -> None:
    _worker_context_box[0] = context


def get_worker_context() -> Any:
    """
    Called from within a worker process (or, under NullParallelizer, the
    main process) by a processing_func passed to run_parallel_with_context().
    """
    return _worker_context_box[0]


def processing_func_wrapper(
    func: MultiprocessingLambdaType, input_arg: Any
) -> Tuple[Optional[Any], Optional[StrictDocChildProcessException]]:
    try:
        result = func(input_arg)
        return result, None
    except Exception as exception_:
        return None, StrictDocChildProcessException(ExceptionInfo(exception_))


class Parallelizer(ABC):
    @staticmethod
    def create(parallelize: bool, *, dynamic: bool = False) -> "Parallelizer":
        """
        `dynamic` must reflect whether the calling process is known to stay
        single-threaded for as long as this Parallelizer lives (a one-shot
        CLI export - `dynamic=False`) or not (a long-lived, multithreaded
        process such as the dev server - `dynamic=True`). See
        MultiprocessingParallelizer.__init__() for what this controls; it is
        a fixed, static choice, not re-evaluated at runtime.
        """
        if parallelize:
            return MultiprocessingParallelizer(dynamic=dynamic)
        return NullParallelizer()

    @abstractmethod
    def run_parallel(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
        on_item_complete: Optional[Callable[[int, Any], None]] = None,
    ) -> Iterable[Any]:
        """
        `on_item_complete`, if given, is called from the caller's own
        process as each item finishes (in completion order, not submission
        order), with the item's original index into `contents` and its
        result - e.g. to drive a live progress indicator without adding a
        return-value contract of its own.
        """
        raise NotImplementedError

    @abstractmethod
    def run_parallel_with_context(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
        context: Any,
        on_item_complete: Optional[Callable[[int, Any], None]] = None,
    ) -> Iterable[Any]:
        """
        Like run_parallel(), but `context` is sent to each worker process
        exactly once instead of being pickled into every task. `processing_func`
        must be a plain, module-level function (not a bound method or a
        closure) that retrieves the context via get_worker_context().
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError


class MultiprocessingParallelizer(Parallelizer):
    def __init__(self, *, dynamic: bool = False) -> None:
        """
        `dynamic` is a fixed, one-time choice for this instance's whole
        lifetime - never re-evaluated per call:

        - dynamic=False (a one-shot CLI export): the process is single-
          threaded for as long as this Parallelizer lives, so "fork" is
          always safe on POSIX (cheapest option - no fresh interpreter
          startup or module re-import per worker, just a copy-on-write
          clone of this already-warmed-up process).
        - dynamic=True (a long-lived, multithreaded process, e.g. the dev
          server): forking a multithreaded process risks a deadlock (a
          lock held by a thread that doesn't exist in the child), so use
          "forkserver" instead (cheap forks from a clean, single-threaded
          server process it maintains separately).

        Neither is available on Windows, where "spawn" is used regardless
        of `dynamic`.

        Exception: PyInstaller/Nuitka-frozen binaries. "spawn"/"forkserver"
        re-invoke sys.executable with an internal bootstrap command line,
        but for a frozen binary sys.executable is the strictdoc executable
        itself, so that bootstrap string gets parsed by strictdoc's own
        argparse CLI and fails (e.g. "invalid choice: 'from
        multiprocessing.forkserver import main; ...'"). The Python docs
        confirm "spawn"/"forkserver" generally cannot be used with frozen
        executables on POSIX and that "fork" may work there instead. So
        frozen binaries keep the "fork" default regardless of `dynamic`.
        """
        process_number: int = multiprocessing.cpu_count()

        if environment.is_github_ci_windows():  # pragma: no cover
            fixed_process_number = 2
            print(  # noqa: T201
                f"MultiprocessingParallelizer: "
                f"Running on GitHub CI Windows with only "
                f"{fixed_process_number} parallel processes instead of "
                f"{process_number}."
            )
            process_number = 2

        if environment.is_binary_dist:
            start_method = "fork"
        elif dynamic:
            start_method = (
                "forkserver"
                if "forkserver" in multiprocessing.get_all_start_methods()
                else "spawn"
            )
        else:
            start_method = (
                "fork"
                if "fork" in multiprocessing.get_all_start_methods()
                else "spawn"
            )
        self.process_number = process_number
        self.mp_context = multiprocessing.get_context(start_method)
        self.executor = ProcessPoolExecutor(
            max_workers=self.process_number, mp_context=self.mp_context
        )

    def run_parallel(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
        on_item_complete: Optional[Callable[[int, Any], None]] = None,
    ) -> Iterable[Any]:
        try:
            future_to_index = {
                self.executor.submit(
                    processing_func_wrapper, processing_func, item
                ): idx
                for idx, item in enumerate(contents)
            }
            results = [None] * len(contents)

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                result = future.result()
                if result[1] is not None:
                    raise result[1]
                results[idx] = result[0]
                if on_item_complete is not None:
                    on_item_complete(idx, result[0])

            return results
        except Exception as e:
            raise e

    def run_parallel_with_context(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
        context: Any,
        on_item_complete: Optional[Callable[[int, Any], None]] = None,
    ) -> Iterable[Any]:
        self.executor.shutdown(wait=True)

        # `context` (e.g. a whole traceability index) can be large - tens to
        # hundreds of MB for a big documentation tree. Pickling it into every
        # worker via a pool initializer (initargs) means each worker pays a
        # full deserialization of that payload, and under "forkserver"/
        # "spawn" those deserializations happen independently and
        # concurrently in every worker, which for a large enough payload
        # turns into severe memory/CPU contention - worse than not
        # parallelizing at all (measured: a 138MB index caused a 12-worker
        # export to run ~3.5x SLOWER than sequential on one real, large
        # document tree).
        #
        # Where self.mp_context is "fork" (always true for a non-dynamic
        # Parallelizer, see __init__ above), sidestep this entirely: set the
        # context in this (parent) process, then fork. Forked children share
        # the already-built object graph via copy-on-write - no pickling of
        # `context` at all, and no redundant per-worker reconstruction.
        # Measured effect on a 138MB-index tree: export dropped from ~98s to
        # ~15s, faster than not parallelizing.
        #
        # The shutdown() above and the rebuild below are both required, not
        # just leftover caution: ProcessPoolExecutor workers, once forked,
        # are long-lived - they don't re-fork per task. If self.executor
        # still held workers forked before _init_worker_context(context)
        # ran (e.g. left over from an earlier run_parallel() call for
        # document reading), those workers' memory would never see the
        # newly-set _worker_context_box[0], since copy-on-write sharing
        # only happens at the moment of forking. So new workers must be
        # forked after the context is set in the parent - which means
        # throwing away any existing pool and creating a new one.
        if self.mp_context.get_start_method() == "fork":
            _init_worker_context(context)
            self.executor = ProcessPoolExecutor(
                max_workers=self.process_number, mp_context=self.mp_context
            )
            return self.run_parallel(
                contents, processing_func, on_item_complete
            )

        # "forkserver"/"spawn" (a dynamic Parallelizer, or Windows - the
        # measured regression above is not a POSIX-only curiosity, it
        # applies there unconditionally, every time, regardless of tree
        # size). Below a modest number of tasks, sending `context` once per
        # worker via the pool initializer is still fine (process_number
        # pickles, not one per task). Above it, skip multiprocessing for
        # this call entirely and run in-process: this is the same safety
        # net this parallelizer relied on (as a document-count cutoff one
        # level up, in html_generator.py) before the fork+COW path existed,
        # now scoped to exactly the cases that cannot use that path.
        if len(contents) > _LARGE_CONTEXT_FALLBACK_THRESHOLD:
            self.executor = ProcessPoolExecutor(
                max_workers=self.process_number, mp_context=self.mp_context
            )
            _init_worker_context(context)
            results = []
            for idx, item in enumerate(contents):
                result = processing_func(item)
                results.append(result)
                if on_item_complete is not None:
                    on_item_complete(idx, result)
            return results

        self.executor = ProcessPoolExecutor(
            max_workers=self.process_number,
            mp_context=self.mp_context,
            initializer=_init_worker_context,
            initargs=(context,),
        )
        return self.run_parallel(contents, processing_func, on_item_complete)

    def shutdown(self) -> None:
        self.executor.shutdown(wait=True)


class NullParallelizer(Parallelizer):
    def run_parallel(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
        on_item_complete: Optional[Callable[[int, Any], None]] = None,
    ) -> Iterable[Any]:
        results = []
        for idx, content in enumerate(contents):
            result = processing_func(content)
            results.append(result)
            if on_item_complete is not None:
                on_item_complete(idx, result)
        return results

    def run_parallel_with_context(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
        context: Any,
        on_item_complete: Optional[Callable[[int, Any], None]] = None,
    ) -> Iterable[Any]:
        _init_worker_context(context)
        return self.run_parallel(contents, processing_func, on_item_complete)

    def shutdown(self) -> None:
        pass
