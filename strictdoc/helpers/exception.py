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
        self.exception = exception
        self.exc_info = sys.exc_info()
        filename, lineno, func, _ = get_exception_origin()
        self.filename = filename
        self.lineno = lineno
        self.func = func

    def print_stack_trace(self) -> None:
        traceback.print_exception(
            *self.exc_info, limit=None, file=sys.stdout, chain=True
        )

    def get_detailed_error_message(self) -> str:
        return (
            f"error: {str(self.exception)}\n"
            f"error source: {self.filename}:{self.lineno}, function: {self.func}()"
        )


class StrictDocException(Exception):
    def __str__(self) -> str:
        return self.to_print_message()

    def to_print_message(self) -> str:
        return str(self.args[0])
