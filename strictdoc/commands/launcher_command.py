"""Launcher command for the Tk-based StrictDoc UI."""

import argparse

from strictdoc.cli.base_command import BaseCommand
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.launcher import main as launcher_main


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
        launcher_main()
