import os
from typing import List, Optional

from strictdoc.cli.command_parser_builder import CommandParserBuilder
from strictdoc.helpers.auto_described import auto_described


class CLIValidationError(Exception):
    pass


class ImportReqIFCommandConfig:
    def __init__(self, input_path: str, output_path: str, profile):
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.profile: Optional[str] = profile


class ManageAutoUIDCommandConfig:
    def __init__(self, *, input_path: str, config_path: Optional[str]):
        self.input_path: str = input_path
        self._config_path: Optional[str] = config_path

    def get_path_to_config(self) -> Optional[str]:
        path_to_input_dir = self.input_path
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        path_to_config = (
            self._config_path
            if self._config_path is not None
            else path_to_input_dir
        )
        return path_to_config

    def validate(self):
        if self._config_path is not None and not os.path.exists(
            self._config_path
        ):
            raise CLIValidationError(
                "Provided path to a configuration file does not exist: "
                f"{self._config_path}"
            )


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
        input_path: str,
        output_path: Optional[str],
        config_path: Optional[str],
        reload: bool,
        port: Optional[int],
    ):
        self._input_path: str = input_path
        self.output_path: Optional[str] = output_path
        self._config_path: Optional[str] = config_path
        self.reload: bool = reload
        self.port: Optional[int] = port

    def get_full_input_path(self):
        return os.path.abspath(self._input_path)

    def get_path_to_config(self):
        return (
            self._config_path
            if self._config_path is not None
            else self._input_path
        )

    def validate(self):
        if not os.path.exists(self._input_path):
            raise CLIValidationError(
                f"Provided input path does not exist: {self._input_path}"
            )

        if self._config_path is not None and not os.path.exists(
            self._config_path
        ):
            raise CLIValidationError(
                "Provided path to a configuration file does not exist: "
                f"{self._config_path}"
            )


@auto_described
class ExportCommandConfig:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        input_paths,
        output_dir: str,
        config_path: Optional[str],
        project_title: Optional[str],
        formats,
        fields,
        no_parallelization,
        enable_mathjax,
        reqif_profile: Optional[str],
        experimental_enable_file_traceability,
    ):
        assert isinstance(input_paths, list), f"{input_paths}"
        self.input_paths: List[str] = input_paths
        self.output_dir: str = output_dir
        self._config_path: Optional[str] = config_path
        self.project_title: Optional[str] = project_title
        self.formats = formats
        self.fields = fields
        self.no_parallelization = no_parallelization
        self.enable_mathjax = enable_mathjax
        self.reqif_profile: Optional[str] = reqif_profile
        self.experimental_enable_file_traceability = (
            experimental_enable_file_traceability
        )
        self.output_html_root: str = os.path.join(output_dir, "html")

    def get_path_to_config(self) -> Optional[str]:
        path_to_input_dir = self.input_paths[0]
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        path_to_config = (
            self._config_path
            if self._config_path is not None
            else path_to_input_dir
        )
        return path_to_config

    def validate(self):
        for input_path_ in self.input_paths:
            if not os.path.exists(input_path_):
                raise CLIValidationError(
                    f"Provided input path does not exist: {input_path_}"
                )
        if self._config_path is not None:
            if not os.path.exists(self._config_path):
                raise CLIValidationError(
                    "Provided path to a configuration file does not exist: "
                    f"{self._config_path}"
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

    @property
    def is_manage_autouid_command(self):
        return (
            self.args.command == "manage" and self.args.subcommand == "auto-uid"
        )

    def get_passthrough_config(self) -> PassthroughCommandConfig:
        return PassthroughCommandConfig(
            self.args.input_file, self.args.output_file
        )

    def get_export_config(self) -> ExportCommandConfig:
        project_title: Optional[str] = self.args.project_title

        output_dir = self.args.output_dir if self.args.output_dir else "output"
        if not os.path.isabs(output_dir):
            cwd = os.getcwd()
            output_dir = os.path.join(cwd, output_dir)

        return ExportCommandConfig(
            self.args.input_paths,
            output_dir,
            self.args.config,
            project_title,
            self.args.formats,
            self.args.fields,
            self.args.no_parallelization,
            self.args.enable_mathjax,
            self.args.reqif_profile,
            self.args.experimental_enable_file_traceability,
        )

    def get_import_config_reqif(self, _) -> ImportReqIFCommandConfig:
        return ImportReqIFCommandConfig(
            self.args.input_path, self.args.output_path, self.args.profile
        )

    def get_manage_autouid_config(self) -> ManageAutoUIDCommandConfig:
        return ManageAutoUIDCommandConfig(
            input_path=self.args.input_path,
            config_path=self.args.config,
        )

    def get_import_config_excel(self, _) -> ImportExcelCommandConfig:
        return ImportExcelCommandConfig(
            self.args.input_path, self.args.output_path, self.args.parser
        )

    def get_server_config(self) -> ServerCommandConfig:
        return ServerCommandConfig(
            input_path=self.args.input_path,
            output_path=self.args.output_path,
            config_path=self.args.config,
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
