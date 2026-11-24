import asyncio
from typing import Any, Dict, List

from strictdoc.server.app import ignore_connection_reset_on_windows


class FakeEventLoop(asyncio.AbstractEventLoop):
    def __init__(self) -> None:
        self.default_handler_contexts: List[Dict[str, Any]] = []

    def default_exception_handler(self, context: Dict[str, Any]) -> None:
        self.default_handler_contexts.append(context)


def test_connection_reset_error_is_not_reported():
    loop = FakeEventLoop()
    context = {
        "message": (
            "Exception in callback "
            "_ProactorBasePipeTransport._call_connection_lost(None)"
        ),
        "exception": ConnectionResetError(
            10054,
            "An existing connection was forcibly closed by the remote host",
        ),
    }

    ignore_connection_reset_on_windows(loop, context)

    assert loop.default_handler_contexts == []


def test_other_errors_go_to_the_default_handler():
    loop = FakeEventLoop()
    context_with_other_error = {
        "message": "Exception in callback",
        "exception": ValueError("Some other error"),
    }
    context_without_exception = {"message": "Task was destroyed"}

    ignore_connection_reset_on_windows(loop, context_with_other_error)
    ignore_connection_reset_on_windows(loop, context_without_exception)

    assert loop.default_handler_contexts == [
        context_with_other_error,
        context_without_exception,
    ]
