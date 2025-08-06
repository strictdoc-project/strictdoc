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

        self.executor = ProcessPoolExecutor(max_workers=process_number)

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
