import contextlib
import shutil
import sys
import time
from functools import wraps
from typing import Callable, Iterator, List, Optional, TypeVar

from typing_extensions import ParamSpec

from strictdoc import environment
from strictdoc.helpers.math import round_up

P = ParamSpec("P")
R = TypeVar("R")


class SimpleNominalExit(Exception):
    """
    A custom exception used for situations when we don't want to print the final
    performance result at the end of function execution.

    The use case for this: StrictDoc's "about" and "version" commands that do
    not need the performance result (total execution time) to be printed.
    """

    pass


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


def _format_measure_performance_line(title: str, time_diff: float) -> str:
    padded_name = f"{title} ".ljust(60, ".")
    padded_time = f" {time_diff:0.2f}".rjust(6, ".")
    return f"{padded_name}{padded_time}s"


@contextlib.contextmanager
def measure_performance(title: str) -> Iterator[None]:
    time_start = time.time()
    try:
        yield
    except SimpleNominalExit:
        return

    time_end = time.time()

    time_diff = time_end - time_start
    print(  # noqa: T201
        _format_measure_performance_line(title, time_diff), flush=True
    )


@contextlib.contextmanager
def measure_performance_loop(
    prefix: str, total: int
) -> Iterator[Callable[..., "contextlib.AbstractContextManager[None]"]]:
    """
    Like measure_performance(), but for calls made repeatedly in a loop.

    Each item is reported via a short title (e.g. a bare file name), which
    is combined with `prefix` for display. Under --debug, this reconstructs
    exactly what `measure_performance(f"{prefix}: {title}")` would have
    printed, so existing --debug output is unaffected. Otherwise, if stdout
    is a terminal, prints a single line that is overwritten in place for
    each item; if stdout is not a terminal (piped/redirected), prints one
    summary line up front, then a "." per completed item, ending with a
    newline once the loop is done.

    Usage is normally `with report_progress(title): ...`, timing the body
    of the `with` block. When the work already happened elsewhere (e.g. in
    a worker process) and only its already-measured duration is being
    reported, pass `elapsed_time` explicitly and use an empty block:
    `with report_progress(title, elapsed_time=elapsed): pass`.
    """
    is_debug_mode = environment.is_debug_mode
    is_tty = sys.stdout.isatty()
    index = 0
    printed_progress_line = False

    if not is_debug_mode and not is_tty:
        print(f"{prefix}: {total} tasks", flush=True)  # noqa: T201

    @contextlib.contextmanager
    def report_progress(
        title: str,
        elapsed_time: Optional[float] = None,
        short_title: Optional[str] = None,
    ) -> Iterator[None]:
        """
        short_title, if given, is used only for the in-place tty progress
        line below: --debug output always shows the full title, since it is
        printed once per item rather than overwritten in place.
        """
        nonlocal index, printed_progress_line
        index += 1
        time_start = time.time()
        try:
            yield
        except SimpleNominalExit:
            return

        time_diff = (
            elapsed_time
            if elapsed_time is not None
            else (time.time() - time_start)
        )

        if is_debug_mode:
            print(  # noqa: T201
                _format_measure_performance_line(
                    f"{prefix}: {title}", time_diff
                ),
                flush=True,
            )
            return

        if not is_tty:
            print(".", end="", flush=True)  # noqa: T201
            printed_progress_line = True
            return

        display_title = short_title if short_title is not None else title
        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
        line = f"{prefix}: {index}/{total}: {display_title}"[
            : terminal_width - 1
        ]
        print(f"\r\x1b[K{line}", end="", flush=True)  # noqa: T201
        printed_progress_line = True

    try:
        yield report_progress
    finally:
        if printed_progress_line:
            print(flush=True)  # noqa: T201


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
