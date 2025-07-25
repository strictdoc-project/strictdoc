"""
Run StrictDoc child tasks as separate processes.

The current implementation is based on a combination of APIs:
- The child processes are created using multiprocessing.Process. Each process
  is started with daemon=True which ensures that it is killed in case the parent
  process itself terminates due to an unexpected error or exception.
- The parent communicates with the child processes using multiprocessing.Queue().

The previous implementation did not work because it did not handle the following
cases correctly:

- When a child process exists unexpectedly.
- When a child process raises exception.

def map_does_not_work(self, contents, processing_func):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        return executor.map(processing_func, contents)
"""

import atexit
import multiprocessing
import sys
from abc import ABC, abstractmethod
from queue import Empty
from typing import Any, Callable, Iterable, Optional, Tuple, Union

from strictdoc import environment
from strictdoc.helpers.coverage import register_code_coverage_hook
from strictdoc.helpers.exception import (
    ExceptionInfo,
    StrictDocException,
)

MultiprocessingLambdaType = Callable[[Any], Any]


# Marker used by a child process to notify the parent process that it has failed.
CHILD_PROCESS_FAILED = "CHILD_PROCESS_FAILED"


class Parallelizer(ABC):
    @staticmethod
    def create(parallelize: bool) -> "Parallelizer":
        if parallelize:
            return MultiprocessingParallelizer()
        return NullParallelizer()

    @abstractmethod
    def run_parallel(
        self,
        contents: Iterable[Any],
        processing_func: MultiprocessingLambdaType,
    ) -> Iterable[Any]:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> bool:
        raise NotImplementedError


class MultiprocessingParallelizer(Parallelizer):
    def __init__(self) -> None:
        # @sdoc[SDOC_IMPL_2]
        try:
            self.input_queue: multiprocessing.Queue[
                Union[Tuple[int, Any, MultiprocessingLambdaType], None]
            ] = multiprocessing.Queue()
            self.output_queue: multiprocessing.Queue[Tuple[int, Any]] = (
                multiprocessing.Queue()
            )

            #
            # FIXME: Debugging:
            #        Bug: Process parallelization has become flaky on Windows (rarely) #2121
            #        https://github.com/strictdoc-project/strictdoc/issues/2121
            #        Move this to a dedicated --processes argument.
            #
            process_number: int = multiprocessing.cpu_count()

            if environment.is_github_ci_windows():  # pragma: no cover
                fixed_process_number = 2
                print(  # noqa: T201
                    f"Parallelizer: "
                    f"Running on GitHub CI Windows with only "
                    f"{fixed_process_number} parallel processes instead of "
                    f"{process_number}."
                )
                process_number = fixed_process_number

            self.processes = [
                multiprocessing.Process(
                    target=MultiprocessingParallelizer._run,
                    args=(self.input_queue, self.output_queue),
                    daemon=False,
                )
                for _ in range(0, process_number)
            ]

            self.at_least_one_child_process_failed: bool = False

            for process in self.processes:
                process.start()
        except OSError as exception:  # pragma: no cover
            raise OSError(
                "OSError when initializing the Parallelizer. "
                f"Underlying exception: {exception}"
            ) from None
        # @sdoc[/SDOC_IMPL_2]

    def shutdown(self) -> bool:
        bad_child_exit_code: bool = False

        # @sdoc[SDOC_IMPL_2]
        # macOS edge case: If the __init__ fails to initialize itself, we may
        # end up having no self.processes attribute at all.
        was_fully_initialized = hasattr(self, "processes")
        # @sdoc[/SDOC_IMPL_2]

        if was_fully_initialized:
            for _ in self.processes:
                self.input_queue.put(None)

            for process_ in self.processes:
                # Before forcing the child process to terminate, wait with join()
                # to let the child process exit by itself.
                process_.join(timeout=2)
                if process_.is_alive():
                    print(  # noqa: T201
                        f"error: Parallelizer: Process PID {process_.pid} "
                        f"failed to join within timeout.",
                        flush=True,
                    )
                    process_.terminate()
                    process_.join()

            for process_ in self.processes:
                if process_.exitcode != 0:
                    print(  # noqa: T201
                        "error: Parallelizer: Child process status: "
                        f"PID: {process_.pid}, exit code: {process_.exitcode}.",
                        flush=True,
                    )
                    bad_child_exit_code = True
        else:  # pragma: no cover
            pass

        # It is important that these queue methods are called otherwise the
        # process can get stuck without termination on Windows. This issue
        # caused many flaky test runs on GitHub CI Actions.
        # https://github.com/strictdoc-project/strictdoc/issues/2083
        self.input_queue.close()
        self.output_queue.close()
        self.input_queue.cancel_join_thread()
        self.output_queue.cancel_join_thread()

        # On Windows GitHub CI, there is sometimes a strange random edge case where
        # no child process has failed prematurely but there is at least one
        # child process that is reported with a non-realistic exit code:
        # error: Parallelizer: Child process status: PID: 6624, exit code: 3221356611.
        # Exiting with 1 only it is known that a child process has failed and
        # ignoring the bad exit codes otherwise.
        if bad_child_exit_code and self.at_least_one_child_process_failed:
            return False

        return True

    def run_parallel(
        self,
        contents: Iterable[Any],
        processing_func: MultiprocessingLambdaType,
    ) -> Iterable[Any]:
        size = 0
        for content_idx, content in enumerate(contents):
            self.input_queue.put((content_idx, content, processing_func))
            size += 1
        results = []
        while size > 0:
            try:
                result = self.output_queue.get(block=True, timeout=0.1)
                if result[1] == CHILD_PROCESS_FAILED:
                    self.at_least_one_child_process_failed = True
                    raise StrictDocException(
                        "Parallelizer: One of the child processes "
                        "has exited prematurely."
                    ) from None
                results.append(result)
                size -= 1
            except Empty:
                if any(process.exitcode for process in self.processes):
                    self.at_least_one_child_process_failed = True
                    raise StrictDocException(
                        "Parallelizer: One of the child processes "
                        "has exited prematurely."
                    ) from None
        return map(lambda r: r[1], sorted(results, key=lambda r: r[0]))

    @staticmethod
    def _run(
        input_queue: "multiprocessing.Queue[Tuple[int, Any, MultiprocessingLambdaType]]",
        output_queue: "multiprocessing.Queue[Tuple[int, Any]]",
    ) -> None:
        register_code_coverage_hook()

        def close_queues_() -> None:  # pragma: no cover
            """
            Close the multiprocessing queues owned by the child process.

            It is important that these queue methods are called otherwise the
            process can get stuck without termination as tested on both Windows
            and macOS. This issue caused many flaky test runs on GitHub CI Actions.
            https://github.com/strictdoc-project/strictdoc/issues/2083

            Both close() and cancel_join_thread() check if they need to be called,
            so assuming that this method can be called multiple times as well.
            """

            input_queue.close()
            output_queue.close()
            input_queue.cancel_join_thread()
            output_queue.cancel_join_thread()

        def exit_hook_() -> None:
            close_queues_()

        atexit.register(exit_hook_)

        exception_info: Optional[ExceptionInfo] = None

        while True:
            content_idx = -1
            try:
                item = input_queue.get(block=True)
                # The parent signals this child process to terminate peacefully.
                # Stopping the infinite loop without signalling any error.
                if item is None:
                    break

                content_idx, content, processing_func = item
                result = processing_func(content)
                output_queue.put((content_idx, result))
            except Exception as exception_:  # pragma: no cover
                output_queue.put((content_idx, CHILD_PROCESS_FAILED))

                exception_info = ExceptionInfo(exception_)

                break

        close_queues_()
        sys.stdout.flush()
        sys.stderr.flush()

        if exception_info is None:
            sys.exit(0)
        else:  # pragma: no cover
            if environment.is_debug_mode:
                exception_info.print_stack_trace()
            print(  # noqa: T201
                exception_info.get_detailed_error_message(), flush=True
            )
            sys.exit(1)


class NullParallelizer(Parallelizer):
    def run_parallel(
        self,
        contents: Iterable[Any],
        processing_func: MultiprocessingLambdaType,
    ) -> Iterable[Any]:
        results = []
        for content in contents:
            results.append(processing_func(content))
        return results

    def shutdown(self) -> bool:
        return True
