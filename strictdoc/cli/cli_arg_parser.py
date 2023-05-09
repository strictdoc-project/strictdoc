import argparse
import os
import sys
from enum import Enum
from typing import List, Optional

from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.cli.argument_int_range import IntRange
from strictdoc.core.environment import SDocRuntimeEnvironment
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.helpers.auto_described import auto_described

EXPORT_FORMATS = ["html", "html-standalone", "rst", "excel", "reqif-sdoc"]
EXCEL_PARSERS = ["basic"]


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
        print(f"{self.prog}: error: {message}", file=sys.stderr)  # noqa: T201
        print("")  # noqa: T201
        print("Further help:")  # noqa: T201
        print(  # noqa: T201
            "'strictdoc -h/--help' provides a general overview of available commands."  # noqa: E501
        )
        print(  # noqa: T201
            "'strictdoc <command> -h/--help' provides command-specific help."
        )
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

    # Command – About
    _ = command_subparsers.add_parser(
        "about",
        help="About StrictDoc.",
        description="About StrictDoc.",
        formatter_class=formatter,
    )

    # Command – Export
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

    # Command – Import
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
        if parser not in ReqIFProfile.ALL:
            message = (
                f"invalid choice: '{parser}' (choose from {ReqIFProfile.ALL})"
            )
            raise argparse.ArgumentTypeError(message)
        return parser

    command_parser_import_reqif.add_argument(
        "profile",
        type=check_reqif_parser,
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

    # Command: Import -> Excel
    command_parser_import_excel = command_parser_import_subparsers.add_parser(
        "excel",
        help="Create StrictDoc file from Excel document.",
        description="Create StrictDoc file Excel ReqIF document.",
        formatter_class=formatter,
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

    # Command – Passthrough
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

    # Command – Dump Grammar
    command_parser_dump_grammar = command_subparsers.add_parser(
        "dump-grammar",
        help="Dump the SDoc grammar to a .tx file.",
        formatter_class=formatter,
    )
    command_parser_dump_grammar.add_argument(
        "output_file", type=str, help="Path to the output .tx file"
    )

    # Command – Server
    command_parser_server = command_subparsers.add_parser(
        "server",
        help="Run StrictDoc Web server.",
        description="Run StrictDoc Web server.",
        formatter_class=formatter,
    )
    command_parser_server.add_argument("input_path")
    command_parser_server.add_argument("--output-path", type=str)
    command_parser_server.add_argument(
        "--reload", default=False, action="store_true"
    )
    command_parser_server.add_argument(
        "--no-reload", dest="reload", action="store_false"
    )
    command_parser_server.add_argument("--port", type=IntRange(1024, 65000))

    # Command – Version
    command_subparsers.add_parser(
        "version",
        help="Print the version of StrictDoc.",
        formatter_class=formatter,
    )
    return main_parser


class ImportReqIFCommandConfig:
    def __init__(self, input_path: str, output_path: str, profile):
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.profile: Optional[str] = profile


class ImportExcelCommandConfig:
    def __init__(self, input_path, output_path, parser):
        self.input_path = input_path
        self.output_path = output_path
        self.parser = parser


class PassthroughCommandConfig:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file


@auto_described
class ServerCommandConfig:
    def __init__(
        self,
        *,
        environment: SDocRuntimeEnvironment,
        input_path: str,
        output_path: Optional[str],
        reload: bool,
        port: Optional[int],
    ):
        assert os.path.exists(input_path)
        self.environment: SDocRuntimeEnvironment = environment
        abs_input_path = os.path.abspath(input_path)
        self.input_path: str = abs_input_path
        self.output_path: Optional[str] = output_path
        self.reload: bool = reload
        self.port: Optional[int] = port


class ExportMode(Enum):
    DOCTREE = 1
    STANDALONE = 2
    DOCTREE_AND_STANDALONE = 3


class ExportCommandConfig:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        environment: SDocRuntimeEnvironment,
        input_paths,
        output_dir: str,
        project_title: Optional[str],
        formats,
        fields,
        no_parallelization,
        enable_mathjax,
        experimental_enable_file_traceability,
    ):
        assert isinstance(input_paths, list), f"{input_paths}"
        self.environment: SDocRuntimeEnvironment = environment
        self.input_paths: List[str] = input_paths
        self.output_dir: str = output_dir
        self.project_title: Optional[str] = project_title
        self.formats = formats
        self.fields = fields
        self.no_parallelization = no_parallelization
        self.enable_mathjax = enable_mathjax
        self.experimental_enable_file_traceability = (
            experimental_enable_file_traceability
        )
        self.output_html_root: str = os.path.join(output_dir, "html")

        self.is_running_on_server = False

        # This option comes from the project config when the
        # config file is read.
        self.dir_for_sdoc_assets: str = ""

        # FIXME: This does not belong here.
        self._server_host: Optional[str] = None
        self._server_port: Optional[int] = None

    @property
    def server_host(self) -> str:
        assert self._server_host is not None
        return self._server_host

    @property
    def server_port(self) -> int:
        assert self._server_port is not None
        return self._server_port

    def get_export_mode(self):
        if "html" in self.formats:
            if "html-standalone" in self.formats:
                return ExportMode.DOCTREE_AND_STANDALONE
            return ExportMode.DOCTREE
        if "html-standalone" in self.formats:
            return ExportMode.STANDALONE
        raise NotImplementedError

    @property
    def strictdoc_root_path(self):
        return self.environment.path_to_strictdoc

    def get_static_files_path(self):
        return self.environment.get_static_files_path()

    def get_extra_static_files_path(self):
        return self.environment.get_extra_static_files_path()

    def integrate_configs(
        self,
        *,
        project_config: ProjectConfig,
        server_config: Optional[ServerCommandConfig],
    ):
        server_port = project_config.server_port
        if server_config is not None:
            self.is_running_on_server = True
            if server_config.port is not None:
                server_port = server_config.port
        self._server_port = server_port

        if self.project_title is None:
            self.project_title = project_config.project_title
        self.dir_for_sdoc_assets = project_config.dir_for_sdoc_assets
        self.experimental_enable_file_traceability = (
            self.experimental_enable_file_traceability
            or project_config.is_feature_activated(
                ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
            )
        )
        self._server_host = project_config.server_host


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

    def get_export_config(
        self, environment: SDocRuntimeEnvironment
    ) -> ExportCommandConfig:
        assert isinstance(environment, SDocRuntimeEnvironment)
        project_title: Optional[str] = self.args.project_title

        output_dir = self.args.output_dir if self.args.output_dir else "output"
        if not os.path.isabs(output_dir):
            cwd = os.getcwd()
            output_dir = os.path.join(cwd, output_dir)

        return ExportCommandConfig(
            environment,
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
            self.args.input_path, self.args.output_path, self.args.profile
        )

    def get_import_config_excel(self, _) -> ImportExcelCommandConfig:
        return ImportExcelCommandConfig(
            self.args.input_path, self.args.output_path, self.args.parser
        )

    def get_server_config(
        self, environment: SDocRuntimeEnvironment
    ) -> ServerCommandConfig:
        assert isinstance(environment, SDocRuntimeEnvironment), environment
        return ServerCommandConfig(
            environment=environment,
            input_path=self.args.input_path,
            output_path=self.args.output_path,
            reload=self.args.reload,
            port=self.args.port,
        )

    def get_dump_grammar_config(self) -> DumpGrammarCommandConfig:
        return DumpGrammarCommandConfig(output_file=self.args.output_file)


def create_sdoc_args_parser(testing_args=None) -> SDocArgsParser:
    args = testing_args
    if not args:
        parser = cli_args_parser()
        args = parser.parse_args()
    return SDocArgsParser(args)
