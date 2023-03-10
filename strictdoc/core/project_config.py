import os

import toml

from strictdoc.helpers.auto_described import auto_described


@auto_described
class ProjectConfig:
    DEFAULT_PROJECT_TITLE = "Untitled Project"
    DEFAULT_DIR_FOR_SDOC_ASSETS = "_static"

    def __init__(self, project_title: str, dir_for_sdoc_assets: str):
        self.project_title: str = project_title
        self.dir_for_sdoc_assets: str = dir_for_sdoc_assets

    @staticmethod
    def default_config():
        return ProjectConfig(
            project_title=ProjectConfig.DEFAULT_PROJECT_TITLE,
            dir_for_sdoc_assets=ProjectConfig.DEFAULT_DIR_FOR_SDOC_ASSETS,
        )


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

        project_title = ProjectConfig.DEFAULT_PROJECT_TITLE
        dir_for_sdoc_assets = ProjectConfig.DEFAULT_DIR_FOR_SDOC_ASSETS

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

        if "project" in config_content:
            project_content = config_content["project"]
            project_title = project_content.get("title", project_title)
            dir_for_sdoc_assets = project_content.get(
                "html_assets_strictdoc_dir", dir_for_sdoc_assets
            )
        return ProjectConfig(
            project_title=project_title,
            dir_for_sdoc_assets=dir_for_sdoc_assets,
        )
