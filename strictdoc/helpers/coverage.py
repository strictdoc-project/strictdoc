import atexit
import os
import signal
import types
from typing import Optional


def register_code_coverage_hook() -> None:
    if not "COVERAGE_PROCESS_START" in os.environ:
        # This branch will never be checked by the coverage.
        return  # pragma: no cover

    import coverage  # noqa: PLC0415

    current_coverage = coverage.Coverage.current()

    assert current_coverage is not None

    def save_coverage() -> None:
        print(  # noqa: T201
            "strictdoc/server: exit hook: saving code coverage...",
            flush=True,
        )
        current_coverage.stop()
        # Code coverage is stopped at this point. Marking the next line to
        # be excluded from code coverage.
        current_coverage.save()  # pragma: no cover

    atexit.register(save_coverage)

    def handle_signal(
        signum: int,
        frame: Optional[types.FrameType],  # noqa: ARG001
    ) -> None:
        print(  # noqa: T201
            f"strictdoc: caught signal {signum}.", flush=True
        )
        save_coverage()
        # Code coverage is stopped at this point. Marking the next line to
        # be excluded from code coverage.
        signal.signal(signum, signal.SIG_DFL)  # pragma: no cover
        os.kill(os.getpid(), signum)  # pragma: no cover

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_signal)
