"""
@relation(SDOC-SRS-163, scope=file)
"""

import argparse

import strictdoc
from strictdoc.cli.base_command import BaseCommand
from strictdoc.helpers.parallelizer import Parallelizer


class VersionCommand(BaseCommand):
    HELP = "Print the version of StrictDoc."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        pass

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        print(strictdoc.__version__)  # noqa: T201
