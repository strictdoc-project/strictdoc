# mypy: disable-error-code="arg-type,attr-defined,no-any-return,no-untyped-call,no-untyped-def,var-annotated,type-arg"
import datetime
import os
import re
import sys
from enum import Enum
from typing import List, Optional, Tuple

import toml

from strictdoc import SDocRuntimeEnvironment
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.cli.cli_arg_parser import (
    ExportCommandConfig,
    ServerCommandConfig,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.path_filter import validate_mask


def parse_relation_tuple(column_name: str) -> Optional[Tuple]:
    match_result = re.search(
        r"^((Parent|Child|File)?)(\[(.{1,32})])?$", column_name
    )
    if match_result is None:
        return None
    return match_result.group(1), match_result.group(4)


class ProjectFeature(str, Enum):
    # Stable features.
    TABLE_SCREEN = "TABLE_SCREEN"
    TRACEABILITY_SCREEN = "TRACEABILITY_SCREEN"
    DEEP_TRACEABILITY_SCREEN = "DEEP_TRACEABILITY_SCREEN"

    MATHJAX = "MATHJAX"

    # Experimental features.
    SEARCH = "SEARCH"
    HTML2PDF = "HTML2PDF"
    REQIF = "REQIF"
    DIFF = "DIFF"
    PROJECT_STATISTICS_SCREEN = "PROJECT_STATISTICS_SCREEN"
    STANDALONE_DOCUMENT_SCREEN = "STANDALONE_DOCUMENT_SCREEN"
    TRACEABILITY_MATRIX_SCREEN = "TRACEABILITY_MATRIX_SCREEN"
    REQUIREMENT_TO_SOURCE_TRACEABILITY = "REQUIREMENT_TO_SOURCE_TRACEABILITY"

    MERMAID = "MERMAID"
    RAPIDOC = "RAPIDOC"
    NESTOR = "NESTOR"

    ALL_FEATURES = "ALL_FEATURES"

    @staticmethod
    def all():  # noqa: A003
        return list(map(lambda c: c.value, ProjectFeature))


@auto_described
class ProjectConfig:  # pylint: disable=too-many-instance-attributes
    DEFAULT_PROJECT_TITLE = "Untitled Project"
    DEFAULT_DIR_FOR_SDOC_ASSETS = "_static"
    DEFAULT_FEATURES: List[str] = [
        ProjectFeature.TABLE_SCREEN,
        ProjectFeature.TRACEABILITY_SCREEN,
        ProjectFeature.DEEP_TRACEABILITY_SCREEN,
        ProjectFeature.SEARCH,
    ]
    DEFAULT_SERVER_HOST = "127.0.0.1"
    DEFAULT_SERVER_PORT = 5111

    def __init__(
        self,
        environment: SDocRuntimeEnvironment,
        project_title: str,
        dir_for_sdoc_assets: str,
        project_features: List[str],
        server_host: str,
        server_port: int,
        include_doc_paths: List[str],
        exclude_doc_paths: List[str],
        source_root_path: Optional[str],
        include_source_paths: List[str],
        exclude_source_paths: List[str],
        html2pdf_template: Optional[str],
        traceability_matrix_relation_columns: Optional[
            List[Tuple[str, Optional[str]]]
        ],
        reqif_profile: str,
        reqif_multiline_is_xhtml: bool,
        reqif_enable_mid: bool,
        reqif_import_markup: Optional[str],
        config_last_update: Optional[datetime.datetime],
        chromedriver: Optional[str],
    ):
        assert isinstance(environment, SDocRuntimeEnvironment)
        if source_root_path is not None:
            assert os.path.isdir(source_root_path), source_root_path
            assert os.path.isabs(source_root_path), source_root_path

        self.environment: SDocRuntimeEnvironment = environment

        # Settings obtained from the strictdoc.toml config file.
        self.project_title: str = project_title
        self.dir_for_sdoc_assets: str = dir_for_sdoc_assets
        self.project_features: List[str] = project_features
        self.server_host: str = server_host
        self.server_port: int = server_port
        self.include_doc_paths: List[str] = include_doc_paths
        self.exclude_doc_paths: List[str] = exclude_doc_paths
        self.source_root_path: Optional[str] = source_root_path
        self.include_source_paths: List[str] = include_source_paths
        self.exclude_source_paths: List[str] = exclude_source_paths

        # Settings derived from the command-line parameters.

        # Common settings
        self.input_paths: Optional[List[str]] = None
        self.output_dir: str = "output"

        # Export action.
        self.export_output_html_root: Optional[str] = None
        self.export_formats: Optional[List[str]] = None
        self.export_included_documents: bool = False
        self.generate_bundle_document: bool = False
        self.filter_requirements: Optional[str] = None
        self.filter_sections: Optional[str] = None
        self.free_text_to_text: bool = False

        self.excel_export_fields: Optional[List[str]] = None

        self.html2pdf_template: Optional[str] = html2pdf_template

        self.traceability_matrix_relation_columns: Optional[
            List[Tuple[str, Optional[str]]]
        ] = traceability_matrix_relation_columns
        self.reqif_profile: str = reqif_profile
        self.reqif_multiline_is_xhtml: bool = reqif_multiline_is_xhtml
        self.reqif_enable_mid: bool = reqif_enable_mid
        self.reqif_import_markup: Optional[str] = reqif_import_markup

        self.autouuid_include_sections: bool = False

        self.config_last_update: Optional[datetime.datetime] = (
            config_last_update
        )
        self.is_running_on_server: bool = False
        self.view: Optional[str] = None
        self.chromedriver: Optional[str] = chromedriver

    @staticmethod
    def default_config(environment: SDocRuntimeEnvironment):
        assert isinstance(environment, SDocRuntimeEnvironment)
        return ProjectConfig(
            environment=environment,
            project_title=ProjectConfig.DEFAULT_PROJECT_TITLE,
            dir_for_sdoc_assets=ProjectConfig.DEFAULT_DIR_FOR_SDOC_ASSETS,
            project_features=ProjectConfig.DEFAULT_FEATURES,
            server_host=ProjectConfig.DEFAULT_SERVER_HOST,
            server_port=ProjectConfig.DEFAULT_SERVER_PORT,
            include_doc_paths=[],
            exclude_doc_paths=[],
            source_root_path=None,
            include_source_paths=[],
            exclude_source_paths=[],
            html2pdf_template=None,
            traceability_matrix_relation_columns=None,
            reqif_profile=ReqIFProfile.P01_SDOC,
            reqif_multiline_is_xhtml=False,
            reqif_enable_mid=False,
            reqif_import_markup=None,
            config_last_update=None,
            chromedriver=None,
        )

    # Some server command settings can override the project config settings.
    def integrate_server_config(self, server_config: ServerCommandConfig):
        self.is_running_on_server = True
        if server_config.port is not None:
            server_port = server_config.port
            self.server_port = server_port

    def integrate_export_config(self, export_config: ExportCommandConfig):
        if export_config.project_title is not None:
            self.project_title = export_config.project_title
        self.input_paths = export_config.input_paths
        self.output_dir = export_config.output_dir
        self.export_output_html_root = export_config.output_html_root
        self.export_formats = export_config.formats
        self.export_included_documents = export_config.included_documents
        self.generate_bundle_document = export_config.generate_bundle_document
        self.free_text_to_text = export_config.free_text_to_text
        self.filter_requirements = export_config.filter_requirements
        self.filter_sections = export_config.filter_sections
        self.excel_export_fields = export_config.fields
        self.view = export_config.view
        self.chromedriver = export_config.chromedriver
        if self.source_root_path is None:
            source_root_path = export_config.input_paths[0]
            if not os.path.abspath(source_root_path):
                source_root_path = os.path.abspath(source_root_path)
            source_root_path = source_root_path.rstrip("/")
            self.source_root_path = source_root_path

        if (
            export_config.enable_mathjax
            and ProjectFeature.MATHJAX not in self.project_features
        ):
            self.project_features.append(ProjectFeature.MATHJAX)

        if export_config.reqif_profile is not None:
            self.reqif_profile = export_config.reqif_profile

        # If the TOML file sets this to True, ignore what is in CLI.
        if not self.reqif_multiline_is_xhtml:
            self.reqif_multiline_is_xhtml = (
                export_config.reqif_multiline_is_xhtml
            )
        if not self.reqif_enable_mid:
            self.reqif_enable_mid = export_config.reqif_enable_mid

    def is_feature_activated(self, feature: ProjectFeature):
        return feature in self.project_features

    def is_activated_table_screen(self):
        return ProjectFeature.TABLE_SCREEN in self.project_features

    def is_activated_trace_screen(self):
        return ProjectFeature.TRACEABILITY_SCREEN in self.project_features

    def is_activated_deep_trace_screen(self):
        return ProjectFeature.DEEP_TRACEABILITY_SCREEN in self.project_features

    def is_activated_project_statistics(self):
        return ProjectFeature.PROJECT_STATISTICS_SCREEN in self.project_features

    def is_activated_requirements_to_source_traceability(self):
        return (
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
            in self.project_features
        )

    def is_activated_requirements_coverage(self):
        return (
            ProjectFeature.TRACEABILITY_MATRIX_SCREEN in self.project_features
        )

    def is_activated_standalone_document(self):
        return (
            ProjectFeature.STANDALONE_DOCUMENT_SCREEN in self.project_features
        )

    def is_activated_search(self):
        return (
            self.is_running_on_server
            and ProjectFeature.SEARCH in self.project_features
        )

    def is_activated_html2pdf(self) -> bool:
        return ProjectFeature.HTML2PDF in self.project_features

    def is_activated_diff(self) -> bool:
        return ProjectFeature.DIFF in self.project_features

    def is_activated_reqif(self) -> bool:
        return ProjectFeature.REQIF in self.project_features

    def is_activated_mathjax(self) -> bool:
        return ProjectFeature.MATHJAX in self.project_features

    def is_activated_mermaid(self) -> bool:
        return ProjectFeature.MERMAID in self.project_features

    def is_activated_rapidoc(self) -> bool:
        return ProjectFeature.RAPIDOC in self.project_features

    def get_strictdoc_root_path(self) -> str:
        return self.environment.path_to_strictdoc

    def get_static_files_path(self) -> str:
        return self.environment.get_static_files_path()

    def get_extra_static_files_path(self) -> str:
        return self.environment.get_extra_static_files_path()


class ProjectConfigLoader:
    @staticmethod
    def load_from_path_or_get_default(
        *,
        path_to_config: str,
        environment: SDocRuntimeEnvironment,
    ) -> ProjectConfig:
        if not os.path.exists(path_to_config):
            return ProjectConfig.default_config(environment=environment)
        if os.path.isdir(path_to_config):
            path_to_config = os.path.join(path_to_config, "strictdoc.toml")
        if not os.path.isfile(path_to_config):
            return ProjectConfig.default_config(environment=environment)

        try:
            config_content = toml.load(path_to_config)
        except toml.decoder.TomlDecodeError as exception:
            raise StrictDocException(  # noqa: T201
                f"Could not parse the config file {path_to_config}: "
                f"{exception}."
            ) from None
        except Exception as exception:
            raise NotImplementedError from exception

        config_last_update = get_file_modification_time(path_to_config)

        return ProjectConfigLoader._load_from_dictionary(
            config_dict=config_content,
            environment=environment,
            config_last_update=config_last_update,
            path_to_config=path_to_config,
        )

    @staticmethod
    def load_from_string(
        *, toml_string: str, environment: SDocRuntimeEnvironment
    ) -> ProjectConfig:
        config_dict = toml.loads(toml_string)
        return ProjectConfigLoader._load_from_dictionary(
            config_dict=config_dict,
            environment=environment,
            config_last_update=None,
            path_to_config=None,
        )

    @staticmethod
    def _load_from_dictionary(
        *,
        config_dict: dict,
        environment: SDocRuntimeEnvironment,
        config_last_update: Optional[datetime.datetime],
        path_to_config: Optional[str],
    ) -> ProjectConfig:
        if path_to_config is not None:
            assert os.path.isfile(path_to_config), path_to_config
            if not os.path.abspath(path_to_config):
                path_to_config = os.path.abspath(path_to_config)

        project_title = ProjectConfig.DEFAULT_PROJECT_TITLE
        dir_for_sdoc_assets = ProjectConfig.DEFAULT_DIR_FOR_SDOC_ASSETS
        project_features = ProjectConfig.DEFAULT_FEATURES
        server_host = ProjectConfig.DEFAULT_SERVER_HOST
        server_port = ProjectConfig.DEFAULT_SERVER_PORT
        include_doc_paths = []
        exclude_doc_paths = []
        source_root_path = None
        include_source_paths = []
        exclude_source_paths = []
        html2pdf_template: Optional[str] = None
        traceability_matrix_relation_columns: Optional[List[Tuple]] = None
        reqif_profile = ReqIFProfile.P01_SDOC
        reqif_multiline_is_xhtml = False
        reqif_enable_mid = False
        reqif_import_markup: Optional[str] = None
        chromedriver: Optional[str] = None

        if "project" in config_dict:
            project_content = config_dict["project"]
            project_title = project_content.get("title", project_title)
            dir_for_sdoc_assets = project_content.get(
                "html_assets_strictdoc_dir", dir_for_sdoc_assets
            )
            project_features = project_content.get("features", project_features)
            if not isinstance(project_features, list):
                print(  # noqa: T201
                    f"error: strictdoc.toml: 'feature' parameter must be an "
                    f"array: '{project_features}'."
                )
                sys.exit(1)

            for feature in project_features:
                if feature not in ProjectFeature.all():
                    print(  # noqa: T201
                        f"error: strictdoc.toml: unknown feature declared: "
                        f"'{feature}'."
                    )
                    sys.exit(1)
            if ProjectFeature.ALL_FEATURES in project_features:
                project_features = ProjectFeature.all()

            include_doc_paths = project_content.get(
                "include_doc_paths", include_doc_paths
            )
            assert isinstance(include_doc_paths, list)
            for include_doc_path in include_doc_paths:
                try:
                    validate_mask(include_doc_path)
                except SyntaxError as exception:
                    print(  # noqa: T201
                        f"error: strictdoc.toml: 'include_doc_paths': "
                        f"{exception} Provided string: '{include_doc_path}'."
                    )
                    sys.exit(1)

            exclude_doc_paths = project_content.get(
                "exclude_doc_paths", exclude_doc_paths
            )
            assert isinstance(exclude_doc_paths, list)
            for exclude_doc_path in exclude_doc_paths:
                try:
                    validate_mask(exclude_doc_path)
                except SyntaxError as exception:
                    print(  # noqa: T201
                        f"error: strictdoc.toml: 'exclude_doc_paths': "
                        f"{exception} Provided string: '{exclude_doc_path}'."
                    )
                    sys.exit(1)

            source_root_path = project_content.get(
                "source_root_path", source_root_path
            )
            if source_root_path is not None:
                original_source_root_path = source_root_path
                if (
                    not os.path.isabs(source_root_path)
                    and path_to_config is not None
                ):
                    source_root_path = os.path.join(
                        os.path.dirname(path_to_config), source_root_path
                    )
                    source_root_path = os.path.abspath(source_root_path)
                if not os.path.isdir(source_root_path):
                    print(  # noqa: T201
                        f"error: strictdoc.toml: 'source_root_path': "
                        f"Provided path does not exist: "
                        f"{original_source_root_path}."
                    )
                    sys.exit(1)
                if not os.path.isabs(source_root_path):
                    source_root_path = os.path.abspath(source_root_path)
            include_source_paths = project_content.get(
                "include_source_paths", include_source_paths
            )
            assert isinstance(include_source_paths, list)
            for include_source_path in include_source_paths:
                try:
                    validate_mask(include_source_path)
                except SyntaxError as exception:
                    print(  # noqa: T201
                        f"error: strictdoc.toml: 'include_source_paths': "
                        f"{exception} Provided string: '{include_source_path}'."
                    )
                    sys.exit(1)

            exclude_source_paths = project_content.get(
                "exclude_source_paths", exclude_source_paths
            )
            assert isinstance(exclude_source_paths, list)
            for exclude_source_path in exclude_source_paths:
                try:
                    validate_mask(exclude_source_path)
                except SyntaxError as exception:
                    print(  # noqa: T201
                        f"error: strictdoc.toml: 'exclude_source_paths': "
                        f"{exception} Provided string: '{exclude_source_path}'."
                    )
                    sys.exit(1)

            html2pdf_template = project_content.get(
                "html2pdf_template", html2pdf_template
            )
            if html2pdf_template is not None:
                assert not os.path.isabs(html2pdf_template)
                if path_to_config is not None:
                    path_to_config_dir = os.path.dirname(path_to_config)
                    html2pdf_template = os.path.join(
                        path_to_config_dir, html2pdf_template
                    )
                if not os.path.isfile(html2pdf_template):
                    print(  # noqa: T201
                        "error: strictdoc.toml: 'html2pdf_template': "
                        f"invalid path to a template file: {html2pdf_template}'."
                    )
                    sys.exit(1)

            traceability_matrix_relation_columns_config: Optional[List] = (
                project_content.get(
                    "traceability_matrix_relation_columns", None
                )
            )
            if traceability_matrix_relation_columns_config is not None:
                assert isinstance(
                    traceability_matrix_relation_columns_config, list
                )
                traceability_matrix_relation_columns = []
                for (
                    relation_column_string_
                ) in traceability_matrix_relation_columns_config:
                    relation_tuple = parse_relation_tuple(
                        relation_column_string_
                    )
                    assert relation_tuple is not None
                    traceability_matrix_relation_columns.append(relation_tuple)

            chromedriver = project_content.get("chromedriver", chromedriver)
            if chromedriver is not None and not os.path.isfile(chromedriver):
                print(  # noqa: T201
                    f"warning: strictdoc.toml: chromedriver {chromedriver} "
                    "not found."
                )

        if "server" in config_dict:
            # FIXME: Introduce at least a basic validation for the host/port.
            server_content = config_dict["server"]
            server_host = server_content.get("host", server_host)
            server_port = server_content.get("port", server_port)
            assert (
                isinstance(server_port, int) and 1024 < server_port < 65000
            ), server_port

        if "reqif" in config_dict:
            # FIXME: Introduce at least a basic validation.
            reqif_content = config_dict["reqif"]
            reqif_multiline_is_xhtml = reqif_content.get(
                "multiline_is_xhtml", False
            )
            assert isinstance(reqif_multiline_is_xhtml, bool), reqif_content

            # FIXME
            reqif_enable_mid = reqif_content.get("enable_mid", False)
            assert isinstance(reqif_enable_mid, bool), reqif_content

            # FIXME
            reqif_import_markup = reqif_content.get("import_markup", None)
            if reqif_import_markup is not None:
                assert (
                    reqif_import_markup in SDocMarkup.ALL
                ), reqif_import_markup

        return ProjectConfig(
            environment=environment,
            project_title=project_title,
            dir_for_sdoc_assets=dir_for_sdoc_assets,
            project_features=project_features,
            server_host=server_host,
            server_port=server_port,
            include_doc_paths=include_doc_paths,
            exclude_doc_paths=exclude_doc_paths,
            source_root_path=source_root_path,
            include_source_paths=include_source_paths,
            exclude_source_paths=exclude_source_paths,
            html2pdf_template=html2pdf_template,
            traceability_matrix_relation_columns=traceability_matrix_relation_columns,
            reqif_profile=reqif_profile,
            reqif_multiline_is_xhtml=reqif_multiline_is_xhtml,
            reqif_enable_mid=reqif_enable_mid,
            reqif_import_markup=reqif_import_markup,
            config_last_update=config_last_update,
            chromedriver=chromedriver,
        )
