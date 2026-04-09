"""Launcher command for the Tk-based StrictDoc UI."""

import argparse
import importlib.util

from strictdoc.cli.base_command import BaseCommand
from strictdoc.helpers.parallelizer import Parallelizer


def is_launcher_available() -> bool:
    return (
        importlib.util.find_spec("tkinter") is not None
        and importlib.util.find_spec("_tkinter") is not None
    )


class LauncherCommand(BaseCommand):
    HELP = "Launch StrictDoc's desktop launcher (experimental)."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:  # noqa: ARG003
        # No additional arguments for now. If needed, they can be
        # added here later (for example, to pass a default workspace).
        pass

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        # Delegate to the Tkinter launcher entry point.
        from strictdoc.features.launcher.launcher_frame import (  # noqa: PLC0415
            main as launcher_main,
        )

        launcher_main()
