"""
@relation(SDOC-SRS-163, scope=file)
"""

import argparse

import strictdoc
from strictdoc.cli.base_command import BaseCommand
from strictdoc.helpers.parallelizer import Parallelizer


class AboutCommand(BaseCommand):
    HELP = "About StrictDoc."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        pass

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        print("=============")  # noqa: T201
        print("= StrictDoc =")  # noqa: T201
        print("=============")  # noqa: T201
        print(  # noqa: T201
            "Purpose: Software for writing technical requirements specifications."
        )
        print(f"Version: {strictdoc.__version__}")  # noqa: T201
        print(  # noqa: T201
            "Docs:    https://strictdoc.readthedocs.io/en/stable/"
        )
        print(  # noqa: T201
            "GitHub:  https://github.com/strictdoc-project/strictdoc"
        )
        print("License: Apache 2")  # noqa: T201
