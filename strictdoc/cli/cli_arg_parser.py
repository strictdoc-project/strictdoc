import argparse
import os
import sys
from enum import Enum
from typing import List

EXPORT_FORMATS = ["html", "html-standalone", "rst", "excel", "reqif-sdoc"]

REQIF_PARSERS = ["sdoc"]


def _check_formats(formats):
    formats_array = formats.split(",")
    for fmt in formats_array:
        if fmt in EXPORT_FORMATS:
            continue
        export_formats = ", ".join(map(lambda f: f"'{f}'", EXPORT_FORMATS))
        message = f"invalid choice: '{fmt}' (choose from {export_formats})"
        raise argparse.ArgumentTypeError(message)
    return formats_array


def _parse_fields(fields):
    fields_array = fields.split(",")
    return fields_array


class SDocArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        print("")
        print("Further help:")
        print(
            "'strictdoc -h/--help' provides a general overview of available commands."  # noqa: E501
        )
        print("'strictdoc <command> -h/--help' provides command-specific help.")
        sys.exit(2)


def cli_args_parser() -> argparse.ArgumentParser:
    def formatter(prog):
        return argparse.RawTextHelpFormatter(
            prog, indent_increment=2, max_help_position=4, width=80
        )

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
    command_subparsers = main_parser.add_subparsers(
        title="command", dest="command"
    )
    command_subparsers.required = True

    # Command: About
    _ = command_subparsers.add_parser(
        "about",
        help="About StrictDoc.",
        description="About StrictDoc.",
        formatter_class=formatter,
    )

    # Command: Export
    command_parser_export = command_subparsers.add_parser(
        "export",
        help="Export document tree.",
        description=(
            "Export command: "
            "input SDoc documents are generated into HTML and other formats."
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
        help="Export fields, only used for Excel export",
    )
    command_parser_export.add_argument(
        "--fields",
        type=_parse_fields,
        default=["uid", "statement", "parent"],
        help="Export formats",
    )
    command_parser_export.add_argument(
        "--no-parallelization",
        action="store_true",
        help=(
            "Disables parallelization. All work happens in the main thread. "
            "This option might be useful for debugging."
        ),
    )
    command_parser_export.add_argument(
        "--enable-mathjax",
        action="store_true",
        help="Enables Mathjax support (only HTML export).",
    )
    command_parser_export.add_argument(
        "--experimental-enable-file-traceability",
        action="store_true",
        help=(
            "Experimental feature: "
            "enables traceability between requirements and files "
            "(warning: implementation is not complete)."
        ),
    )

    # Command: Import
    command_parser_import = command_subparsers.add_parser(
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
    command_parser_import_reqif = command_parser_import_subparsers.add_parser(
        "reqif",
        help="Create StrictDoc file from ReqIF document.",
        description="Create StrictDoc file from ReqIF document.",
        formatter_class=formatter,
    )

    def check_reqif_parser(parser):
        if parser not in REQIF_PARSERS:
            message = (
                f"invalid choice: '{parser}' (choose from {REQIF_PARSERS})"
            )
            raise argparse.ArgumentTypeError(message)
        return parser

    command_parser_import_reqif.add_argument(
        "parser",
        type=check_reqif_parser,
        help=(
            "An argument that selects the ReqIF parser. "
            f"Possible values: {{{', '.join(REQIF_PARSERS)}}}"
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

    # Command: Import -> Excel
    command_parser_import_excel = command_parser_import_subparsers.add_parser(
        "excel",
        help="Create StrictDoc file from Excel document.",
        description="Create StrictDoc file Excel ReqIF document.",
        formatter_class=formatter,
    )

    def check_excel_parser(parser):
        excel_parsers = ["basic"]
        if parser not in excel_parsers:
            message = (
                f"invalid choice: '{parser}' (choose from {excel_parsers})"
            )
            raise argparse.ArgumentTypeError(message)
        return parser

    command_parser_import_excel.add_argument(
        "parser",
        type=check_excel_parser,
        help=(
            "An argument that selects the ReqIF parser. "
            f"Possible values: {{{', '.join(REQIF_PARSERS)}}}"
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

    # Command: Passthrough
    command_parser_passthrough = command_subparsers.add_parser(
        "passthrough",
        help="Read an SDoc file, then output it again. (used for testing)",
        formatter_class=formatter,
    )
    command_parser_passthrough.add_argument(
        "input_file", type=str, help="Path to the input SDoc file"
    )

    command_parser_passthrough.add_argument(
        "--output-file", type=str, help="Path to the output SDoc file"
    )

    # Command: Dump Grammar
    command_parser_dump_grammar = command_subparsers.add_parser(
        "dump-grammar",
        help="Dump the SDoc grammar to a .tx file.",
        formatter_class=formatter,
    )
    command_parser_dump_grammar.add_argument(
        "output_file", type=str, help="Path to the output .tx file"
    )

    # Command: Server
    command_parser_server = command_subparsers.add_parser(
        "server",
        help="Run StrictDoc Web server.",
        description="Run StrictDoc Web server.",
        formatter_class=formatter,
    )
    command_parser_server.add_argument("input_path")
    command_parser_server.add_argument(
        "--output-path", default="/tmp/strictdoc/output", type=str
    )
    command_parser_server.add_argument(
        "--reload", default=False, action="store_true"
    )
    command_parser_server.add_argument(
        "--no-reload", dest="reload", action="store_false"
    )

    # Command: Version
    command_subparsers.add_parser(
        "version",
        help="Print the version of StrictDoc.",
        formatter_class=formatter,
    )
    return main_parser


class ImportReqIFCommandConfig:
    def __init__(self, input_path, output_path, parser):
        self.input_path = input_path
        self.output_path = output_path
        self.parser = parser


class ImportExcelCommandConfig:
    def __init__(self, input_path, output_path, parser):
        self.input_path = input_path
        self.output_path = output_path
        self.parser = parser


class PassthroughCommandConfig:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file


class ServerCommandConfig:
    def __init__(self, *, input_path: str, output_path: str, reload: bool):
        assert os.path.exists(input_path)
        abs_input_path = os.path.abspath(input_path)
        self.input_path: str = abs_input_path
        self.output_path: str = output_path
        self.reload: bool = reload


class ExportMode(Enum):
    DOCTREE = 1
    STANDALONE = 2
    DOCTREE_AND_STANDALONE = 3


class ExportCommandConfig:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        strictdoc_root_path,
        input_paths,
        output_dir: str,
        project_title,
        formats,
        fields,
        no_parallelization,
        enable_mathjax,
        experimental_enable_file_traceability,
    ):
        assert isinstance(input_paths, list), f"{input_paths}"
        self.strictdoc_root_path = strictdoc_root_path
        self.input_paths: List[str] = input_paths
        self.output_dir: str = output_dir
        self.project_title = project_title
        self.formats = formats
        self.fields = fields
        self.no_parallelization = no_parallelization
        self.enable_mathjax = enable_mathjax
        self.experimental_enable_file_traceability = (
            experimental_enable_file_traceability
        )
        self.output_html_root: str = os.path.join(output_dir, "html")

        self.is_running_on_server = False

    def get_export_mode(self):
        if "html" in self.formats:
            if "html-standalone" in self.formats:
                return ExportMode.DOCTREE_AND_STANDALONE
            return ExportMode.DOCTREE
        if "html-standalone" in self.formats:
            return ExportMode.STANDALONE
        raise NotImplementedError

    def get_static_files_path(self):
        if getattr(sys, "frozen", False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            bundle_dir = sys._MEIPASS  # pylint: disable=protected-access
            return os.path.join(bundle_dir, "_static")
        return os.path.join(
            self.strictdoc_root_path, "strictdoc/export/html/_static"
        )

    def get_extra_static_files_path(self):
        if getattr(sys, "frozen", False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            bundle_dir = sys._MEIPASS  # pylint: disable=protected-access
            return os.path.join(bundle_dir, "_static_extra")
        return os.path.join(
            self.strictdoc_root_path, "strictdoc/export/html/_static_extra"
        )


class DumpGrammarCommandConfig:
    def __init__(self, output_file):
        self.output_file = output_file


class SDocArgsParser:
    def __init__(self, args):
        self.args = args

    @property
    def is_about_command(self):
        return self.args.command == "about"

    @property
    def is_passthrough_command(self):
        return self.args.command == "passthrough"

    @property
    def is_export_command(self):
        return self.args.command == "export"

    @property
    def is_import_command_reqif(self):
        return (
            self.args.command == "import" and self.args.import_format == "reqif"
        )

    @property
    def is_import_command_excel(self):
        return (
            self.args.command == "import" and self.args.import_format == "excel"
        )

    @property
    def is_server_command(self):
        return self.args.command == "server"

    @property
    def is_dump_grammar_command(self):
        return self.args.command == "dump-grammar"

    @property
    def is_version_command(self):
        return self.args.command == "version"

    def get_passthrough_config(self) -> PassthroughCommandConfig:
        return PassthroughCommandConfig(
            self.args.input_file, self.args.output_file
        )

    def get_export_config(self, strictdoc_root_path) -> ExportCommandConfig:
        project_title = (
            self.args.project_title
            if self.args.project_title
            else "Untitled Project"
        )

        output_dir = self.args.output_dir if self.args.output_dir else "output"
        if not os.path.isabs(output_dir):
            cwd = os.getcwd()
            output_dir = os.path.join(cwd, output_dir)

        return ExportCommandConfig(
            strictdoc_root_path,
            self.args.input_paths,
            output_dir,
            project_title,
            self.args.formats,
            self.args.fields,
            self.args.no_parallelization,
            self.args.enable_mathjax,
            self.args.experimental_enable_file_traceability,
        )

    def get_import_config_reqif(self, _) -> ImportReqIFCommandConfig:
        return ImportReqIFCommandConfig(
            self.args.input_path, self.args.output_path, self.args.parser
        )

    def get_import_config_excel(self, _) -> ImportExcelCommandConfig:
        return ImportExcelCommandConfig(
            self.args.input_path, self.args.output_path, self.args.parser
        )

    def get_server_config(self) -> ServerCommandConfig:
        return ServerCommandConfig(
            input_path=self.args.input_path,
            output_path=self.args.output_path,
            reload=self.args.reload,
        )

    def get_dump_grammar_config(self) -> DumpGrammarCommandConfig:
        return DumpGrammarCommandConfig(output_file=self.args.output_file)


def create_sdoc_args_parser(testing_args=None) -> SDocArgsParser:
    args = testing_args
    if not args:
        parser = cli_args_parser()
        args = parser.parse_args()
    return SDocArgsParser(args)
