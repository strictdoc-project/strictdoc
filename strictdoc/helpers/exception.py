import sys
import traceback
from typing import Tuple


def get_exception_origin() -> Tuple[str, int, str, str]:
    """
    Get the last traceback entry where the exception occurred.
    """

    tb = traceback.extract_tb(sys.exc_info()[2])[-1]
    filename, lineno, func, text = tb
    return filename, lineno, func, text


class ExceptionInfo:
    def __init__(self, exception: Exception):
        # Store the rendered message, not the exception object itself:
        # ExceptionInfo is sent from a worker process to the parent via
        # StrictDocChildProcessException (see parallelizer.py), and an
        # exception object is only picklable if its class round-trips
        # through Exception's default __reduce__ (`type(exc)(*exc.args)`).
        # Custom StrictDoc exceptions with a keyword-only or otherwise
        # non-trivial __init__ (e.g. StrictDocSemanticError) don't, so
        # keeping a live reference here would make ExceptionInfo itself
        # unpicklable and turn a normal, reportable error into an opaque
        # BrokenProcessPool crash instead. A plain string has no such
        # requirement and is all get_detailed_error_message() ever needed.
        self.exception_message = str(exception)

        filename, lineno, func, _ = get_exception_origin()
        self.filename = filename
        self.lineno = lineno
        self.func = func

        exc_type, exc_value, exc_traceback = sys.exc_info()

        traceback_strings = traceback.format_exception(
            exc_type, exc_value, exc_traceback, limit=None, chain=True
        )

        self.traceback_str = "".join(traceback_strings)

    def get_stack_trace(self) -> str:
        return self.traceback_str

    def get_detailed_error_message(self) -> str:
        return (
            f"error: {self.exception_message}\n"
            f"error source: {self.filename}:{self.lineno}, function: {self.func}()"
        )


class StrictDocException(Exception):
    def __str__(self) -> str:
        return self.to_print_message()

    def to_print_message(self) -> str:
        return str(self.args[0])


class StrictDocChildProcessException(Exception):
    """
    A special custom exception that wraps the ExceptionInfo.

    RATIONALE: This is needed to pass exception information from the child
    process to the parent process. The reason is that ProcessPoolExecutor does
    not propagate the exception stack trace to the parent process. StrictDoc
    captures the child process's trace as ExceptionInfo to address this limitation.
    """

    def __init__(self, exception_info: ExceptionInfo):
        self.exception_info: ExceptionInfo = exception_info
