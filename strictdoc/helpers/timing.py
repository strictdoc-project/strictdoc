# mypy: disable-error-code="no-untyped-def"
import contextlib
from functools import wraps
from time import time
from typing import Any, Callable, TypeVar

from strictdoc.helpers.math import round_up

TimingDecoratorT = TypeVar("TimingDecoratorT", bound=Callable[..., Any])


def timing_decorator(name) -> Callable[[TimingDecoratorT], TimingDecoratorT]:
    def timing_internal(func):
        @wraps(func)
        def wrap(*args, **kw):
            print(f"Step '{name}' start.", flush=True)  # noqa: T201
            time_start = time()
            result = func(*args, **kw)
            time_end = time()
            print(  # noqa: T201
                f"Step '{name}' took: {round_up(time_end - time_start, 2)} sec.",
                flush=True,
            )
            return result

        return wrap

    return timing_internal


@contextlib.contextmanager
def measure_performance(title):
    time_start = time()
    yield
    time_end = time()

    time_diff = time_end - time_start
    padded_name = f"{title} ".ljust(60, ".")
    padded_time = f" {time_diff:0.2f}".rjust(6, ".")
    print(f"{padded_name}{padded_time}s", flush=True)  # noqa: T201
