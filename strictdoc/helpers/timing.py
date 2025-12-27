import contextlib
import time
from functools import wraps
from typing import Callable, Iterator, List, TypeVar

from typing_extensions import ParamSpec

from strictdoc.helpers.math import round_up

P = ParamSpec("P")
R = TypeVar("R")


def timing_decorator(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def timing_internal(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrap(*args: P.args, **kw: P.kwargs) -> R:
            print(f"Step '{name}' start.", flush=True)  # noqa: T201
            time_start = time.time()
            result = func(*args, **kw)
            time_end = time.time()
            print(  # noqa: T201
                f"Step '{name}' took: {round_up(time_end - time_start, 2)} sec.",
                flush=True,
            )
            return result

        return wrap

    return timing_internal


@contextlib.contextmanager
def measure_performance(title: str) -> Iterator[None]:
    time_start = time.time()
    yield
    time_end = time.time()

    time_diff = time_end - time_start
    padded_name = f"{title} ".ljust(60, ".")
    padded_time = f" {time_diff:0.2f}".rjust(6, ".")
    print(f"{padded_name}{padded_time}s", flush=True)  # noqa: T201


@contextlib.contextmanager
def timer(accumulator: List[float]) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        accumulator.append(time.perf_counter() - start)


def timer_print(accumulator: List[float]) -> None:
    print(f"Total match time: {sum(accumulator):.6f}s")  # noqa: T201
    print(  # noqa: T201
        f"Avg per call: {sum(accumulator) / len(accumulator) * 1e6:.2f}µs"
    )
