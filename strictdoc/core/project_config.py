import os
import sys
from enum import Enum
from typing import List

import toml

from strictdoc.helpers.auto_described import auto_described


class ProjectFeature(str, Enum):
    # Stable features.
    TABLE_SCREEN = "TABLE_SCREEN"
    TRACEABILITY_SCREEN = "TRACEABILITY_SCREEN"
    DEEP_TRACEABILITY_SCREEN = "DEEP_TRACEABILITY_SCREEN"

    MATHJAX = "MATHJAX"

    # Experimental features.
    REQIF = "REQIF"
    STANDALONE_DOCUMENT_SCREEN = "STANDALONE_DOCUMENT_SCREEN"
    REQUIREMENTS_COVERAGE_SCREEN = "REQUIREMENTS_COVERAGE_SCREEN"
    REQUIREMENT_TO_SOURCE_TRACEABILITY = "REQUIREMENT_TO_SOURCE_TRACEABILITY"

    @staticmethod
    def all():
        return list(map(lambda c: c.value, ProjectFeature))


@auto_described
class ProjectConfig:
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
        project_title: str,
        dir_for_sdoc_assets: str,
        project_features: List[str],
        server_host: str,
        server_port: int,
    ):
        self.project_title: str = project_title
        self.dir_for_sdoc_assets: str = dir_for_sdoc_assets
        self.project_features: List[str] = project_features
        self.server_host: str = server_host
        self.server_port: int = server_port

    @staticmethod
    def default_config():
        return ProjectConfig(
            project_title=ProjectConfig.DEFAULT_PROJECT_TITLE,
            dir_for_sdoc_assets=ProjectConfig.DEFAULT_DIR_FOR_SDOC_ASSETS,
            project_features=ProjectConfig.DEFAULT_FEATURES,
            server_host=ProjectConfig.DEFAULT_SERVER_HOST,
            server_port=ProjectConfig.DEFAULT_SERVER_PORT,
        )

    def is_feature_activated(self, feature: ProjectFeature):
        return feature in self.project_features

    def is_activated_requirements_to_source_traceability(self):
        return (
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
            in self.project_features
        )

    def is_activated_requirements_coverage(self):
        return (
            ProjectFeature.REQUIREMENTS_COVERAGE_SCREEN in self.project_features
        )

    @staticmethod
    def is_reqif_feature_activated():
        return ProjectFeature.REQIF


class ProjectConfigLoader:
    @staticmethod
    def load_from_path_or_get_default(
        *, path_to_config_dir: str
    ) -> ProjectConfig:
        if not os.path.exists(path_to_config_dir):
            return ProjectConfig.default_config()

        path_to_config = os.path.join(path_to_config_dir, "strictdoc.toml")
        if not os.path.isfile(path_to_config):
            return ProjectConfig.default_config()

        try:
            config_content = toml.load(path_to_config)
        except toml.decoder.TomlDecodeError as exception:
            print(  # noqa: T201
                f"warning: could not parse the config file {path_to_config}: "
                f"{exception}."
            )
            print(  # noqa: T201
                "warning: using default StrictDoc configuration."
            )
            return ProjectConfig.default_config()
        except Exception as exception:
            raise NotImplementedError from exception

        return ProjectConfigLoader._load_from_dictionary(config_content)

    @staticmethod
    def load_from_string(*, toml_string: str) -> ProjectConfig:
        config_dict = toml.loads(toml_string)
        return ProjectConfigLoader._load_from_dictionary(
            config_dict=config_dict
        )

    @staticmethod
    def _load_from_dictionary(config_dict: dict) -> ProjectConfig:
        project_title = ProjectConfig.DEFAULT_PROJECT_TITLE
        dir_for_sdoc_assets = ProjectConfig.DEFAULT_DIR_FOR_SDOC_ASSETS
        project_features = ProjectConfig.DEFAULT_FEATURES
        server_host = ProjectConfig.DEFAULT_SERVER_HOST
        server_port = ProjectConfig.DEFAULT_SERVER_PORT

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

        if "server" in config_dict:
            # FIXME: Introduce at least a basic validation for the host/port.
            server_content = config_dict["server"]
            server_host = server_content.get("host", server_host)
            server_port = server_content.get("port", server_port)
            assert (
                isinstance(server_port, int) and 1024 < server_port < 65000
            ), server_port

        return ProjectConfig(
            project_title=project_title,
            dir_for_sdoc_assets=dir_for_sdoc_assets,
            project_features=project_features,
            server_host=server_host,
            server_port=server_port,
        )
