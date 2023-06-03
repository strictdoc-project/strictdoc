import os
from typing import List, Optional

from strictdoc.cli.command_parser_builder import CommandParserBuilder
from strictdoc.core.environment import SDocRuntimeEnvironment
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.helpers.auto_described import auto_described


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

        if self.experimental_enable_file_traceability:
            deprecation_message = (
                "warning: "
                "'--experimental-enable-file-traceability' command-line "
                "option will be deprecated. Instead, activate the option in "
                "the strictdoc.toml config file as follows:\n"
                "```\n"
                "[project]\n\n"
                "features = [\n"
                '  "REQUIREMENT_TO_SOURCE_TRACEABILITY"\n'
                "]\n"
                "```"
            )
            print(deprecation_message)  # noqa: T201

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
        builder = CommandParserBuilder()
        parser = builder.build()
        args = parser.parse_args()
    return SDocArgsParser(args)
