import argparse
import sys
from typing import Any, Dict, NoReturn

from strictdoc import __version__
from strictdoc.commands.about_command import AboutCommand
from strictdoc.commands.export import ExportCommand
from strictdoc.commands.import_excel import ImportExcelCommand
from strictdoc.commands.import_reqif import ImportReqIFCommand
from strictdoc.commands.manage_autouid_command import ManageAutoUIDCommand
from strictdoc.commands.server import ServerCommand
from strictdoc.commands.version_command import VersionCommand

COMMAND_REGISTRY: Dict[str, Any] = {
    "about": AboutCommand,
    "export": ExportCommand,
    "import": {"excel": ImportExcelCommand, "reqif": ImportReqIFCommand},
    "manage": {"auto-uid": ManageAutoUIDCommand},
    "server": ServerCommand,
    "version": VersionCommand,
}


def formatter(prog: str) -> argparse.RawTextHelpFormatter:
    return argparse.RawTextHelpFormatter(
        prog, indent_increment=2, max_help_position=4, width=80
    )


class SDocArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)  # noqa: T201
        print("")  # noqa: T201
        print("Further help:")  # noqa: T201
        print(  # noqa: T201
            "'strictdoc -h/--help' provides a general overview of available commands."
        )
        print(  # noqa: T201
            "'strictdoc <command> -h/--help' provides command-specific help."
        )
        sys.exit(2)


class CommandParserBuilder:
    def build(self) -> SDocArgumentParser:
        # https://stackoverflow.com/a/19476216/598057
        main_parser = SDocArgumentParser(
            prog="strictdoc",
            add_help=True,
            epilog=(
                """
                Further help: https://strictdoc.readthedocs.io/en/stable/
                """
            ),
        )

        # The -v/--version has a special behavior that it still works when all
        # commands are required == True.
        # https://stackoverflow.com/a/12123598/598057
        main_parser.add_argument(
            "-v", "--version", action="version", version=__version__
        )

        main_parser.add_argument(
            "--debug",
            action="store_true",
            default=False,
            help="Enable more verbose printing of errors when they are encountered.",
        )

        command_subparsers = main_parser.add_subparsers(
            title="command", dest="command"
        )
        command_subparsers.required = True

        # Dynamically add subcommands
        for name, cmd in COMMAND_REGISTRY.items():
            if isinstance(cmd, dict):  # command family
                family_parser = command_subparsers.add_parser(name)
                family_subparsers = family_parser.add_subparsers(
                    dest="subcommand"
                )
                family_subparsers.required = True
                for subname, subcmd in cmd.items():
                    sub_parser = family_subparsers.add_parser(
                        subname,
                        help=subcmd.HELP,
                        description=subcmd.DETAILED_HELP,
                        formatter_class=formatter,
                    )
                    subcmd.add_arguments(sub_parser)
            else:
                cmd_parser = command_subparsers.add_parser(
                    name,
                    help=cmd.HELP,
                    description=cmd.DETAILED_HELP,
                    formatter_class=formatter,
                )
                cmd.add_arguments(cmd_parser)

        return main_parser
