import argparse

from strictdoc.cli.argument_int_range import IntRange
from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.server.server import run_strictdoc_server


class ServerCommand(BaseCommand):
    HELP = "Run StrictDoc web server."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        command_parser_server = parser

        command_parser_server.add_argument("input_path")
        command_parser_server.add_argument("--output-path", type=str)
        command_parser_server.add_argument("--host", type=str)
        command_parser_server.add_argument("--port", type=IntRange(1024, 65000))
        # The --reload and --no-reload options are currently used only for
        # StrictDoc's own development. We may want to revisit this for the end
        # users in the future but for now they are excluded from the help
        # messages.
        command_parser_server.add_argument(
            "--reload",
            default=False,
            action="store_true",
            help=argparse.SUPPRESS,
        )
        command_parser_server.add_argument(
            "--no-reload",
            dest="reload",
            action="store_false",
            help=argparse.SUPPRESS,
        )
        command_parser_server.add_argument(
            "--config",
            type=str,
            help="Path to the StrictDoc TOML config file.",
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config: ServerCommandConfig = ServerCommandConfig(**vars(args))

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        server_config = self.config
        try:
            server_config.validate()
        except CLIValidationError as exception_:
            raise exception_
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=server_config.get_path_to_config(),
        )
        run_strictdoc_server(
            server_config=server_config, project_config=project_config
        )
