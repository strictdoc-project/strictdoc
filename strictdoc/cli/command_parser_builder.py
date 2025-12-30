import argparse
import sys
from typing import Any, Dict, NoReturn, Optional

from strictdoc import __version__
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.commands.about_command import AboutCommand
from strictdoc.commands.export import ExportCommand
from strictdoc.commands.server import ServerCommand
from strictdoc.commands.shared import _check_reqif_profile
from strictdoc.commands.version_command import VersionCommand

EXCEL_PARSERS = ["basic"]


COMMAND_REGISTRY: Dict[str, Any] = {
    "about": AboutCommand,
    "export": ExportCommand,
    "server": ServerCommand,
    "version": VersionCommand,
}


def formatter(prog: str) -> argparse.RawTextHelpFormatter:
    return argparse.RawTextHelpFormatter(
        prog, indent_increment=2, max_help_position=4, width=80
    )


def _check_reqif_import_markup(markup: Optional[str]) -> str:
    if markup is None or markup not in SDocMarkup.ALL:
        valid_text_markups_string = ", ".join(SDocMarkup.ALL)
        message = f"invalid choice: '{markup}' (choose from {valid_text_markups_string})"
        raise argparse.ArgumentTypeError(message)
    return markup


def add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the StrictDoc TOML config file.",
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

        self.add_manage_command(command_subparsers)
        self.add_import_command(command_subparsers)

        # Dynamically add subcommands
        for name, cmd in COMMAND_REGISTRY.items():
            if isinstance(cmd, dict):  # command family
                family_parser = command_subparsers.add_parser(name)
                family_subparsers = family_parser.add_subparsers(
                    dest="subcommand"
                )
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

    @staticmethod
    def add_import_command(
        parent_command_parser: "argparse._SubParsersAction[SDocArgumentParser]",
    ) -> None:
        command_parser_import = parent_command_parser.add_parser(
            "import",
            help="Create StrictDoc files from other formats.",
            description="Create StrictDoc files from other formats.",
            formatter_class=formatter,
        )
        command_parser_import_subparsers = command_parser_import.add_subparsers(
            title="import_format", dest="import_format"
        )
        command_parser_import_subparsers.required = True

        # Command: Import -> ReqIF.
        command_parser_import_reqif = (
            command_parser_import_subparsers.add_parser(
                "reqif",
                help="Create StrictDoc file from ReqIF document.",
                description="Create StrictDoc file from ReqIF document.",
                formatter_class=formatter,
            )
        )

        command_parser_import_reqif.add_argument(
            "profile",
            type=_check_reqif_profile,
            help=(
                "An argument that selects the ReqIF import/export profile. "
                f"Possible values: {{{', '.join(ReqIFProfile.ALL)}}}"
            ),
        )
        command_parser_import_reqif.add_argument(
            "input_path",
            type=str,
            help="Path to the input ReqIF file.",
        )
        command_parser_import_reqif.add_argument(
            "output_path",
            type=str,
            help="Path to the output SDoc file.",
        )
        command_parser_import_reqif.add_argument(
            "--reqif-enable-mid",
            default=False,
            action="store_true",
            help=(
                "Controls whether StrictDoc's MID field will be mapped to ReqIF "
                "SPEC-OBJECT's IDENTIFIER and vice versa when exporting/importing."
            ),
        )
        command_parser_import_reqif.add_argument(
            "--reqif-import-markup",
            default=None,
            type=_check_reqif_import_markup,
            help=(
                "Controls which MARKUP option the imported SDoc documents will have. "
                "This value is RST as what StrictDoc has by default but very often "
                "the requirements tools use the (X)HTML markup for multiline fields in "
                "which case HTML is the best option."
            ),
        )

        # Command: Import -> Excel.
        command_parser_import_excel = (
            command_parser_import_subparsers.add_parser(
                "excel",
                help="Create StrictDoc file from Excel document.",
                description="Create StrictDoc file Excel ReqIF document.",
                formatter_class=formatter,
            )
        )

        def check_excel_parser(parser: str) -> str:
            if parser not in EXCEL_PARSERS:
                message = (
                    f"invalid choice: '{parser}' (choose from {EXCEL_PARSERS})"
                )
                raise argparse.ArgumentTypeError(message)
            return parser

        command_parser_import_excel.add_argument(
            "parser",
            type=check_excel_parser,
            help=(
                "An argument that selects the ReqIF parser. "
                f"Possible values: {{{', '.join(EXCEL_PARSERS)}}}"
            ),
        )
        command_parser_import_excel.add_argument(
            "input_path",
            type=str,
            help="Path to the input ReqIF file.",
        )
        command_parser_import_excel.add_argument(
            "output_path",
            type=str,
            help="Path to the output SDoc file.",
        )

    @staticmethod
    def add_manage_command(
        parent_command_parser: "argparse._SubParsersAction[SDocArgumentParser]",
    ) -> None:
        manage_command_parser = parent_command_parser.add_parser(
            "manage",
            help="Manage StrictDoc project.",
            description="See subcommands to manage StrictDoc project.",
            formatter_class=formatter,
        )
        manage_command_subparsers = manage_command_parser.add_subparsers(
            title="subcommand", dest="subcommand"
        )
        manage_command_subparsers.required = True

        command_parser_auto_uid = manage_command_subparsers.add_parser(
            "auto-uid",
            help="Generates missing requirements UIDs automatically.",
            description=(
                "This command generates missing requirement UID automatically. "
                "The UIDs are generated based on the nearest section "
                "PREFIX (if provided) or the document's "
                'PREFIX (if provided or "REQ-" by default).'
            ),
            formatter_class=formatter,
        )

        command_parser_auto_uid.add_argument(
            "input_path",
            type=str,
            help="Path to the project tree.",
        )
        command_parser_auto_uid.add_argument(
            "--include-sections",
            action="store_true",
            help=(
                "By default, the command only generates the UID for "
                "requirements. This option enables the generation of UID for "
                "sections."
            ),
        )
        add_config_argument(command_parser_auto_uid)
