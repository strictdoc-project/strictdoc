import atexit
import os
import signal
import types
from typing import Optional


def register_code_coverage_hook() -> None:
    if not "COVERAGE_PROCESS_START" in os.environ:
        return

    import coverage

    current_coverage = coverage.Coverage.current()

    if current_coverage:

        def save_coverage() -> None:
            print(  # noqa: T201
                "strictdoc/server: exit hook: saving code coverage...",
                flush=True,
            )
            current_coverage.stop()
            current_coverage.save()

        atexit.register(save_coverage)

        def handle_signal(
            signum: int,
            frame: Optional[types.FrameType],  # noqa: ARG001
        ) -> None:
            print(  # noqa: T201
                f"strictdoc: caught signal {signum}.", flush=True
            )
            save_coverage()
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, handle_signal)
