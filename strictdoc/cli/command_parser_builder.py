# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import argparse
import sys

from strictdoc import __version__
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.cli.argument_int_range import IntRange

EXPORT_FORMATS = [
    "html",
    "html2pdf",
    "rst",
    "json",
    "excel",
    "reqif-sdoc",
    "reqifz-sdoc",
    "sdoc",
    "doxygen",
    "spdx",
]
EXCEL_PARSERS = ["basic"]


def formatter(prog):
    return argparse.RawTextHelpFormatter(
        prog, indent_increment=2, max_help_position=4, width=80
    )


def _check_formats(formats):
    formats_array = formats.split(",")
    for fmt in formats_array:
        if fmt in EXPORT_FORMATS:
            continue
        export_formats = ", ".join(map(lambda f: f"'{f}'", EXPORT_FORMATS))
        message = f"invalid choice: '{fmt}' (choose from {export_formats})"
        raise argparse.ArgumentTypeError(message)
    return formats_array


def _check_reqif_profile(profile):
    if profile not in ReqIFProfile.ALL:
        # To maintain the compatibility with the previous behavior.
        if profile == "sdoc":
            return ReqIFProfile.P01_SDOC
        valid_profiles = ", ".join(map(lambda f: f"'{f}'", ReqIFProfile.ALL))
        message = f"invalid choice: '{profile}' (choose from {valid_profiles})"
        raise argparse.ArgumentTypeError(message)
    return profile


def _check_reqif_import_markup(markup):
    if markup is None:
        return None
    if markup not in SDocMarkup.ALL:
        valid_text_markups_string = ", ".join(SDocMarkup.ALL)
        message = f"invalid choice: '{markup}' (choose from {valid_text_markups_string})"
        raise argparse.ArgumentTypeError(message)
    return markup


def _parse_fields(fields):
    fields_array = fields.split(",")
    return fields_array


def add_config_argument(parser):
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the StrictDoc TOML config file.",
    )


class SDocArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
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
    def build(self) -> argparse.ArgumentParser:
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

        command_subparsers = main_parser.add_subparsers(
            title="command", dest="command"
        )
        command_subparsers.required = True

        self.add_about_command(command_subparsers)
        self.add_export_command(command_subparsers)
        self.add_server_command(command_subparsers)
        self.add_manage_command(command_subparsers)
        self.add_import_command(command_subparsers)
        self.add_version_command(command_subparsers)
        self.add_passthrough_command(command_subparsers)
        self.add_dump_command(command_subparsers)
        self.add_diff_command(command_subparsers)

        return main_parser

    @staticmethod
    def add_about_command(parent_command_parser):
        parent_command_parser.add_parser(
            "about",
            help="About StrictDoc.",
            description="About StrictDoc.",
            formatter_class=formatter,
        )

    @staticmethod
    def add_export_command(parent_command_parser):
        # Command – Export
        command_parser_export = parent_command_parser.add_parser(
            "export",
            help="Export document tree.",
            description=(
                "Export command: "
                "input SDoc documents are generated into "
                "HTML and other formats."
            ),
            formatter_class=formatter,
        )
        command_parser_export.add_argument(
            "input_paths",
            type=str,
            nargs="+",
            help="One or more folders with *.sdoc files",
        )
        command_parser_export.add_argument(
            "--output-dir", type=str, help="Output folder"
        )
        command_parser_export.add_argument(
            "--project-title", type=str, help="Project title"
        )
        command_parser_export.add_argument(
            "--formats",
            type=_check_formats,
            default=["html"],
            help="Export formats",
        )
        command_parser_export.add_argument(
            "--fields",
            type=_parse_fields,
            default=["uid", "statement", "parent"],
            help="Export fields, only used for Excel export",
        )
        command_parser_export.add_argument(
            "--generate-bundle-document",
            action="store_true",
            default=False,
            help=(
                "EXPERIMENTAL: "
                "In addition to generating individual documents, "
                "also create a concatenated bundle that contains "
                "all the documents together."
            ),
        )
        command_parser_export.add_argument(
            "--no-parallelization",
            action="store_true",
            help=(
                "Disables parallelization. "
                "All work happens in the main thread. "
                "This option may be useful for debugging."
            ),
        )
        command_parser_export.add_argument(
            "--enable-mathjax",
            action="store_true",
            help="Enables Mathjax support (only HTML export).",
        )
        command_parser_export.add_argument(
            "--included-documents",
            action="store_true",
            help=(
                "By default the included documents are not exported. "
                "This option makes both including and included documents to be exported."
            ),
        )
        command_parser_export.add_argument(
            "--reqif-profile",
            type=_check_reqif_profile,
            default=ReqIFProfile.P01_SDOC,
            help="Export formats",
        )
        command_parser_export.add_argument(
            "--reqif-multiline-is-xhtml",
            default=False,
            action="store_true",
            help=(
                "Controls whether StrictDoc multiline fields are exported as XHTML "
                "when the option is provided. "
                "By default StrictDoc exports multiline fields with a STRING type."
            ),
        )
        command_parser_export.add_argument(
            "--reqif-enable-mid",
            default=False,
            action="store_true",
            help=(
                "Controls whether StrictDoc's MID field will be mapped to ReqIF "
                "SPEC-OBJECT's IDENTIFIER and vice versa when exporting/importing."
            ),
        )
        command_parser_export.add_argument(
            "--filter-requirements",
            type=str,
            help="Filter which requirements will be exported.",
        )
        command_parser_export.add_argument(
            "--filter-sections",
            type=str,
            help="Filter which sections will be exported.",
        )
        command_parser_export.add_argument(
            "--view",
            type=str,
            help="Choose which view will be exported.",
        )
        command_parser_export.add_argument(
            "--chromedriver",
            type=str,
            help="Path to pre installed chromedriver for html2pdf. "
            "If not given, chromedriver is downloaded and saved to "
            "strictdoc cache.",
        )
        add_config_argument(command_parser_export)

    @staticmethod
    def add_import_command(parent_command_parser):
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

        # Command: Import -> ReqIF
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

        # Command: Import -> Excel
        command_parser_import_excel = (
            command_parser_import_subparsers.add_parser(
                "excel",
                help="Create StrictDoc file from Excel document.",
                description="Create StrictDoc file Excel ReqIF document.",
                formatter_class=formatter,
            )
        )

        def check_excel_parser(parser):
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
    def add_server_command(parent_command_parser):
        command_parser_server = parent_command_parser.add_parser(
            "server",
            help="Run StrictDoc web server.",
            description="Run StrictDoc web server.",
            formatter_class=formatter,
        )
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

        add_config_argument(command_parser_server)

    @staticmethod
    def add_version_command(parent_command_parser):
        parent_command_parser.add_parser(
            "version",
            help="Print the version of StrictDoc.",
            formatter_class=formatter,
        )

    @staticmethod
    def add_passthrough_command(parent_command_parser):
        # passthrough command is kept for backwards compatibility. It will
        # internally be handled as export --formats sdoc.
        command_parser_passthrough = parent_command_parser.add_parser(
            "passthrough",
            help="Read an SDoc file, then output it again. Deprecated, use "
            "strictdoc export --formats sdoc instead.",
            formatter_class=formatter,
        )
        command_parser_passthrough.add_argument(
            "input_paths",
            type=str,
            nargs="+",
            help="One or more folders with *.sdoc files",
        )
        command_parser_passthrough.add_argument(
            "--output-dir",
            type=str,
            help="A directory where to output the SDoc files to.",
        )
        command_parser_passthrough.add_argument(
            "--filter-requirements",
            type=str,
            help="Filter which requirements will be exported.",
        )
        command_parser_passthrough.add_argument(
            "--filter-sections",
            type=str,
            help="Filter which sections will be exported.",
        )
        command_parser_passthrough.add_argument(
            "--view",
            type=str,
            help="Choose which view will be exported.",
        )

        # Hidden default values to make deprecated passthrough parser compatible
        # with SDocArgsParser.get_export_config.
        command_parser_passthrough.add_argument(
            "--project-title", const=None, help=argparse.SUPPRESS
        )
        command_parser_passthrough.add_argument(
            "--formats",
            default=["sdoc"],
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--fields",
            default=None,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--generate-bundle-document",
            default=False,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--no-parallelization",
            default=False,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--enable-mathjax",
            default=False,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--included-documents",
            default=False,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--reqif-profile",
            default=None,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--reqif-multiline-is-xhtml",
            default=False,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--reqif-enable-mid",
            default=False,
            help=argparse.SUPPRESS,
        )
        command_parser_passthrough.add_argument(
            "--chromedriver",
            default=None,
            help=argparse.SUPPRESS,
        )
        add_config_argument(command_parser_passthrough)

    @staticmethod
    def add_dump_command(parent_command_parser):
        command_parser_dump_grammar = parent_command_parser.add_parser(
            "dump-grammar",
            help="Dump the SDoc grammar to a .tx file.",
            formatter_class=formatter,
        )
        command_parser_dump_grammar.add_argument(
            "output_file", type=str, help="Path to the output .tx file"
        )

    @staticmethod
    def add_manage_command(parent_command_parser):
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
                "REQ_PREFIX (if provided) or the document's "
                'REQ_PREFIX (if provided or "REQ-" by default).'
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

    @staticmethod
    def add_diff_command(command_subparsers):
        diff_command_parser = command_subparsers.add_parser(
            "diff",
            help="Generate Diff between two SDoc project trees.",
            formatter_class=formatter,
        )
        diff_command_parser.add_argument(
            "path_to_lhs_tree",
            type=str,
            help="Path to the left-hand side project tree.",
        )
        diff_command_parser.add_argument(
            "path_to_rhs_tree",
            type=str,
            help="Path to the right-hand side project tree.",
        )
        diff_command_parser.add_argument(
            "--output-dir",
            type=str,
            help="A directory where to output the files to.",
        )
