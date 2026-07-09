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
    def create(parallelize: bool) -> "Parallelizer":
        if parallelize:
            return MultiprocessingParallelizer()
        return NullParallelizer()

    @abstractmethod
    def run_parallel(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
    ) -> Iterable[Any]:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError


class MultiprocessingParallelizer(Parallelizer):
    def __init__(self) -> None:
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

        # The implicit "fork" start method forks the whole (multithreaded)
        # interpreter and is deprecated by CPython since 3.12 (raises
        # DeprecationWarning) because it can deadlock in a threaded process;
        # CPython 3.14 switched the POSIX default to "forkserver" for this
        # reason. Use "forkserver" where available (cheap forks from a
        # clean, single-threaded server process) and fall back to "spawn"
        # elsewhere (e.g., Windows).
        #
        # Exception: PyInstaller/Nuitka-frozen binaries. "spawn"/"forkserver"
        # re-invoke sys.executable with an internal bootstrap command line,
        # but for a frozen binary sys.executable is the strictdoc executable
        # itself, so that bootstrap string gets parsed by strictdoc's own
        # argparse CLI and fails (e.g. "invalid choice: 'from
        # multiprocessing.forkserver import main; ...'"). The Python docs
        # confirm "spawn"/"forkserver" generally cannot be used with frozen
        # executables on POSIX and that "fork" may work there instead. So
        # frozen binaries keep the "fork" default.
        if environment.is_binary_dist:
            start_method = "fork"
        else:
            start_method = (
                "forkserver"
                if "forkserver" in multiprocessing.get_all_start_methods()
                else "spawn"
            )
        mp_context = multiprocessing.get_context(start_method)
        self.executor = ProcessPoolExecutor(
            max_workers=process_number, mp_context=mp_context
        )

    def run_parallel(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
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

            return results
        except Exception as e:
            raise e

    def shutdown(self) -> None:
        self.executor.shutdown(wait=True)


class NullParallelizer(Parallelizer):
    def run_parallel(
        self,
        contents: List[Any],
        processing_func: MultiprocessingLambdaType,
    ) -> Iterable[Any]:
        results = []
        for content in contents:
            results.append(processing_func(content))
        return results

    def shutdown(self) -> None:
        pass
