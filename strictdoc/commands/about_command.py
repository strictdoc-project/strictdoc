"""
@relation(SDOC-SRS-163, scope=file)
"""

import argparse

import strictdoc
from strictdoc.cli.base_command import BaseCommand
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.timing import SimpleNominalExit


class AboutCommand(BaseCommand):
    HELP = "About StrictDoc."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        pass

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        width = 72
        border = "=" * width

        lines = [
            f" {'StrictDoc'.center(width - 2)} ",
            "",
            " Purpose: Software for writing technical requirements specifications.",
            "",
            f" Version:      {strictdoc.__version__}",
            " Docs:         https://strictdoc.readthedocs.io/en/stable/",
            " GitHub:       https://github.com/strictdoc-project/strictdoc",
            " Mailing list: https://groups.io/g/strictdoc",
            " License:      Apache 2",
        ]

        banner = (
            f"+{border}+\n"
            + "\n".join(f"|{line.ljust(width)}|" for line in lines)
            + f"\n+{border}+"
        )

        print(banner)  # noqa: T201

        raise SimpleNominalExit
