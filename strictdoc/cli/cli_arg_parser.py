# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import os
from typing import List, Optional

from strictdoc.cli.command_parser_builder import CommandParserBuilder
from strictdoc.helpers.auto_described import auto_described


class CLIValidationError(Exception):
    pass


class ImportReqIFCommandConfig:
    def __init__(
        self,
        input_path: str,
        output_path: str,
        profile: str,
        reqif_enable_mid: bool,
        reqif_import_markup: Optional[str],
    ):
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.profile: Optional[str] = profile
        self.reqif_enable_mid: bool = reqif_enable_mid
        self.reqif_import_markup: Optional[str] = reqif_import_markup


class ManageAutoUIDCommandConfig:
    def __init__(
        self,
        *,
        input_path: str,
        config_path: Optional[str],
        include_sections: bool,
    ):
        self.input_path: str = input_path
        self._config_path: Optional[str] = config_path
        self.include_sections: bool = include_sections

    def get_path_to_config(self) -> str:
        path_to_input_dir: str = self.input_path
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        path_to_config = (
            self._config_path
            if self._config_path is not None
            else path_to_input_dir
        )
        return path_to_config

    def validate(self) -> None:
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

    def get_full_input_path(self) -> str:
        return os.path.abspath(self._input_path)

    def get_path_to_config(self) -> str:
        return (
            self._config_path
            if self._config_path is not None
            else self._input_path
        )

    def validate(self) -> None:
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
    def __init__(
        self,
        input_paths,
        output_dir: str,
        config_path: Optional[str],
        project_title: Optional[str],
        formats,
        fields,
        generate_bundle_document: bool,
        no_parallelization: bool,
        enable_mathjax: bool,
        included_documents: bool,
        filter_requirements: Optional[str],
        filter_sections: Optional[str],
        reqif_profile: Optional[str],
        reqif_multiline_is_xhtml: bool,
        reqif_enable_mid: bool,
        view: Optional[str],
        chromedriver: Optional[str],
        free_text_to_text: bool,
    ):
        assert isinstance(input_paths, list), f"{input_paths}"
        self.input_paths: List[str] = input_paths
        self.output_dir: str = output_dir
        self._config_path: Optional[str] = config_path
        self.project_title: Optional[str] = project_title
        self.formats = formats
        self.fields = fields
        self.generate_bundle_document: bool = generate_bundle_document
        self.no_parallelization: bool = no_parallelization
        self.enable_mathjax: bool = enable_mathjax
        self.included_documents: bool = included_documents
        self.filter_requirements: Optional[str] = filter_requirements
        self.filter_sections: Optional[str] = filter_sections
        self.reqif_profile: Optional[str] = reqif_profile
        self.reqif_multiline_is_xhtml: bool = reqif_multiline_is_xhtml
        self.reqif_enable_mid: bool = reqif_enable_mid
        self.view: Optional[str] = view
        self.output_html_root: str = os.path.join(output_dir, "html")
        self.chromedriver: Optional[str] = chromedriver
        self.free_text_to_text: bool = free_text_to_text

    def get_path_to_config(self) -> str:
        # FIXME: The control flow can be improved.
        path_to_input_dir: str = self.input_paths[0]
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        path_to_config = (
            self._config_path
            if self._config_path is not None
            else path_to_input_dir
        )
        return path_to_config

    def validate(self) -> None:
        for idx_, input_path_ in enumerate(self.input_paths.copy()):
            if not os.path.exists(input_path_):
                raise CLIValidationError(
                    f"Provided input path does not exist: {input_path_}"
                )
            if not os.path.isabs(input_path_):
                self.input_paths[idx_] = os.path.abspath(input_path_).rstrip(
                    "/"
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


class DiffCommandConfig:
    def __init__(
        self,
        path_to_lhs_tree: str,
        path_to_rhs_tree: str,
        output_dir: Optional[str],
    ):
        self.path_to_lhs_tree: str = path_to_lhs_tree
        self.path_to_rhs_tree: str = path_to_rhs_tree
        self.output_dir: Optional[str] = output_dir


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
    def is_diff_command(self):
        return self.args.command == "diff"

    @property
    def is_manage_autouid_command(self):
        return (
            self.args.command == "manage" and self.args.subcommand == "auto-uid"
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
            self.args.generate_bundle_document,
            self.args.no_parallelization,
            self.args.enable_mathjax,
            self.args.included_documents,
            self.args.filter_requirements,
            self.args.filter_sections,
            self.args.reqif_profile,
            self.args.reqif_multiline_is_xhtml,
            self.args.reqif_enable_mid,
            self.args.view,
            self.args.chromedriver,
            self.args.free_text_to_text,
        )

    def get_import_config_reqif(self, _) -> ImportReqIFCommandConfig:
        return ImportReqIFCommandConfig(
            self.args.input_path,
            self.args.output_path,
            self.args.profile,
            self.args.reqif_enable_mid,
            self.args.reqif_import_markup,
        )

    def get_manage_autouid_config(self) -> ManageAutoUIDCommandConfig:
        return ManageAutoUIDCommandConfig(
            input_path=self.args.input_path,
            config_path=self.args.config,
            include_sections=self.args.include_sections,
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

    def get_diff_config(self) -> DiffCommandConfig:
        return DiffCommandConfig(
            path_to_lhs_tree=self.args.path_to_lhs_tree,
            path_to_rhs_tree=self.args.path_to_rhs_tree,
            output_dir=self.args.output_dir,
        )


def create_sdoc_args_parser(testing_args=None) -> SDocArgsParser:
    args = testing_args
    if not args:
        builder = CommandParserBuilder()
        parser = builder.build()
        args = parser.parse_args()
    return SDocArgsParser(args)
