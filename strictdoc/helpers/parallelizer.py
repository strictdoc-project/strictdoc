import multiprocessing
import sys
from abc import ABC, abstractmethod
from queue import Empty
from typing import Any, Callable, Iterable, Tuple

MultiprocessingLambdaType = Callable[[Any], Any]


class Parallelizer(ABC):
    @staticmethod
    def create(parallelize: bool) -> "Parallelizer":
        if parallelize:
            return MultiprocessingParallelizer()
        return NullParallelizer()

    @property
    @abstractmethod
    def parallelization_enabled(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def run_parallel(
        self,
        contents: Iterable[Any],
        processing_func: MultiprocessingLambdaType,
    ) -> Iterable[Any]:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError


class MultiprocessingParallelizer(Parallelizer):
    def __init__(self) -> None:
        # @sdoc[SDOC_IMPL_2]
        try:
            self.input_queue: multiprocessing.Queue[
                Tuple[int, Any, MultiprocessingLambdaType]
            ] = multiprocessing.Queue()
            self.output_queue: multiprocessing.Queue[Tuple[int, Any]] = (
                multiprocessing.Queue()
            )

            self.processes = [
                multiprocessing.Process(
                    target=MultiprocessingParallelizer._run,
                    args=(self.input_queue, self.output_queue),
                )
                for _ in range(0, multiprocessing.cpu_count())
            ]

            for process in self.processes:
                process.start()
        except OSError as exception:
            raise OSError(
                "OSError when initializing the Parallelizer. "
                f"Underlying exception: {exception}"
            ) from None
        # @sdoc[/SDOC_IMPL_2]

    def __del__(self) -> None:
        self.shutdown()

    def shutdown(self) -> None:
        # @sdoc[SDOC_IMPL_2]
        # macOS edge case: If the __init__ fails to initialize itself, we may
        # end up having no self.processes attribute at all.
        was_fully_initialized = hasattr(self, "processes")
        # @sdoc[/SDOC_IMPL_2]

        if was_fully_initialized:
            for process in self.processes:
                process.terminate()

    @property
    def parallelization_enabled(self) -> bool:
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
                results.append(result)
                size -= 1
            except Empty:
                if any(process.exitcode for process in self.processes):
                    print(  # noqa: T201
                        "error: Parallelizer: One of the child processes "
                        "has exited prematurely."
                    )
                    self.shutdown()
                    sys.exit(1)
        return map(lambda r: r[1], sorted(results, key=lambda r: r[0]))

    # This version doesn't handle the following cases properly:
    # - when a child process exists unexpectedly
    # - when a child process raises exception
    # def map_does_not_work(self, contents, processing_func):
    #     with concurrent.futures.ProcessPoolExecutor() as executor:
    #         return executor.map(processing_func, contents)  # noqa: ERA001

    @staticmethod
    def _run(
        input_queue: "multiprocessing.Queue[Tuple[int, Any, MultiprocessingLambdaType]]",
        output_queue: "multiprocessing.Queue[Tuple[int, Any]]",
    ) -> None:
        while True:
            content_idx, content, processing_func = input_queue.get(block=True)
            result = processing_func(content)
            sys.stdout.flush()
            sys.stderr.flush()
            output_queue.put((content_idx, result))


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

    def shutdown(self) -> None:
        pass

    @property
    def parallelization_enabled(self) -> bool:
        return False
