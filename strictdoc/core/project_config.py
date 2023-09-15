import datetime
import os
import sys
from enum import Enum
from typing import List, Optional

import toml

from strictdoc import SDocRuntimeEnvironment
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.cli.cli_arg_parser import (
    ExportCommandConfig,
    ServerCommandConfig,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.path_filter import validate_mask


class ProjectFeature(str, Enum):
    # Stable features.
    TABLE_SCREEN = "TABLE_SCREEN"
    TRACEABILITY_SCREEN = "TRACEABILITY_SCREEN"
    DEEP_TRACEABILITY_SCREEN = "DEEP_TRACEABILITY_SCREEN"

    MATHJAX = "MATHJAX"

    # Experimental features.
    HTML2PDF = "HTML2PDF"
    REQIF = "REQIF"
    PROJECT_STATISTICS_SCREEN = "PROJECT_STATISTICS_SCREEN"
    STANDALONE_DOCUMENT_SCREEN = "STANDALONE_DOCUMENT_SCREEN"
    REQUIREMENTS_COVERAGE_SCREEN = "REQUIREMENTS_COVERAGE_SCREEN"
    REQUIREMENT_TO_SOURCE_TRACEABILITY = "REQUIREMENT_TO_SOURCE_TRACEABILITY"

    MERMAID = "MERMAID"

    ALL_FEATURES = "ALL_FEATURES"

    @staticmethod
    def all():
        return list(map(lambda c: c.value, ProjectFeature))


@auto_described
class ProjectConfig:  # pylint: disable=too-many-instance-attributes
    DEFAULT_PROJECT_TITLE = "Untitled Project"
    DEFAULT_DIR_FOR_SDOC_ASSETS = "_static"
    DEFAULT_FEATURES: List[str] = [
        ProjectFeature.TABLE_SCREEN,
        ProjectFeature.TRACEABILITY_SCREEN,
        ProjectFeature.DEEP_TRACEABILITY_SCREEN,
    ]
    DEFAULT_SERVER_HOST = "127.0.0.1"
    DEFAULT_SERVER_PORT = 5111

    def __init__(  # pylint: disable=too-many-arguments
        self,
        environment: SDocRuntimeEnvironment,
        project_title: str,
        dir_for_sdoc_assets: str,
        project_features: List[str],
        server_host: str,
        server_port: int,
        include_doc_paths: List[str],
        exclude_doc_paths: List[str],
        include_source_paths: List[str],
        exclude_source_paths: List[str],
        reqif_profile: str,
        config_last_update: Optional[datetime.datetime],
    ):
        assert isinstance(environment, SDocRuntimeEnvironment)
        self.environment: SDocRuntimeEnvironment = environment

        # Settings obtained from the strictdoc.toml config file.
        self.project_title: str = project_title
        self.dir_for_sdoc_assets: str = dir_for_sdoc_assets
        self.project_features: List[str] = project_features
        self.server_host: str = server_host
        self.server_port: int = server_port
        self.include_doc_paths: List[str] = include_doc_paths
        self.exclude_doc_paths: List[str] = exclude_doc_paths
        self.include_source_paths: List[str] = include_source_paths
        self.exclude_source_paths: List[str] = exclude_source_paths

        # Settings derived from the command-line parameters.
        # Export action.
        self.export_input_paths: Optional[List[str]] = None
        self.export_output_dir: str = "output"
        self.export_output_html_root: Optional[str] = None
        self.export_formats: Optional[List[str]] = None

        self.excel_export_fields: Optional[List[str]] = None

        self.reqif_profile: str = reqif_profile

        self.config_last_update: Optional[
            datetime.datetime
        ] = config_last_update
        self.is_running_on_server: bool = False

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
            include_source_paths=[],
            exclude_source_paths=[],
            reqif_profile=ReqIFProfile.P01_SDOC,
            config_last_update=None,
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
        self.export_input_paths = export_config.input_paths
        self.export_output_dir = export_config.output_dir
        self.export_output_html_root = export_config.output_html_root
        self.export_formats = export_config.formats
        self.excel_export_fields = export_config.fields

        if (
            export_config.enable_mathjax
            and ProjectFeature.MATHJAX not in self.project_features
        ):
            self.project_features.append(ProjectFeature.MATHJAX)

        if export_config.experimental_enable_file_traceability:
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
            if (
                ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
                not in self.project_features
            ):  # noqa: E501
                self.project_features.append(
                    ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
                )

        if export_config.reqif_profile is not None:
            self.reqif_profile = export_config.reqif_profile

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
            ProjectFeature.REQUIREMENTS_COVERAGE_SCREEN in self.project_features
        )

    def is_activated_standalone_document(self):
        return (
            ProjectFeature.STANDALONE_DOCUMENT_SCREEN in self.project_features
        )

    def is_activated_html2pdf(self) -> bool:
        return ProjectFeature.HTML2PDF in self.project_features

    def is_activated_reqif(self) -> bool:
        return ProjectFeature.REQIF in self.project_features

    def is_activated_mathjax(self) -> bool:
        return ProjectFeature.MATHJAX in self.project_features

    def is_activated_mermaid(self) -> bool:
        return ProjectFeature.MERMAID in self.project_features

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
        )

    @staticmethod
    def _load_from_dictionary(
        *,
        config_dict: dict,
        environment: SDocRuntimeEnvironment,
        config_last_update: Optional[datetime.datetime],
    ) -> ProjectConfig:
        project_title = ProjectConfig.DEFAULT_PROJECT_TITLE
        dir_for_sdoc_assets = ProjectConfig.DEFAULT_DIR_FOR_SDOC_ASSETS
        project_features = ProjectConfig.DEFAULT_FEATURES
        server_host = ProjectConfig.DEFAULT_SERVER_HOST
        server_port = ProjectConfig.DEFAULT_SERVER_PORT
        include_doc_paths = []
        exclude_doc_paths = []
        include_source_paths = []
        exclude_source_paths = []
        reqif_profile = ReqIFProfile.P01_SDOC

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

        if "server" in config_dict:
            # FIXME: Introduce at least a basic validation for the host/port.
            server_content = config_dict["server"]
            server_host = server_content.get("host", server_host)
            server_port = server_content.get("port", server_port)
            assert (
                isinstance(server_port, int) and 1024 < server_port < 65000
            ), server_port

        return ProjectConfig(
            environment=environment,
            project_title=project_title,
            dir_for_sdoc_assets=dir_for_sdoc_assets,
            project_features=project_features,
            server_host=server_host,
            server_port=server_port,
            include_doc_paths=include_doc_paths,
            exclude_doc_paths=exclude_doc_paths,
            include_source_paths=include_source_paths,
            exclude_source_paths=exclude_source_paths,
            reqif_profile=reqif_profile,
            config_last_update=config_last_update,
        )
