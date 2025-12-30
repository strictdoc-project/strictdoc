import argparse
from typing import Any, Dict, Optional

from strictdoc.cli.command_parser_builder import (
    COMMAND_REGISTRY,
    CommandParserBuilder,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.parallelizer import Parallelizer


class SDocArgsParser:
    def __init__(self, args: argparse.Namespace, registry: Dict[str, Any]):
        self.args: argparse.Namespace = args
        self.registry: Dict[str, Any] = registry

    def is_debug_mode(self) -> bool:
        return assert_cast(self.args.debug, bool)

    def run(self, parallelizer: Parallelizer) -> bool:
        if self.args.command not in self.registry:
            return False

        cmd = self.registry[self.args.command]
        if isinstance(cmd, dict):
            assert self.args.subcommand in cmd
            command_instance = cmd[self.args.subcommand](self.args)
        else:
            command_instance = cmd(self.args)
        command_instance.run(parallelizer)

        return True


def create_sdoc_args_parser(
    testing_args: Optional[argparse.Namespace] = None,
) -> SDocArgsParser:
    args = testing_args
    if not args:
        builder = CommandParserBuilder()
        parser = builder.build()
        args = parser.parse_args()
    return SDocArgsParser(args, COMMAND_REGISTRY)
