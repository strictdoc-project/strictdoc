import os
import pickle

import toml


class ProjectConfig:
    DEFAULT_PROJECT_TITLE = "Untitled Project"

    def __init__(self, project_title: str):
        self.project_title: str = project_title

    def dump_to_string(self) -> str:
        return pickle.dumps(self, 0).decode(encoding="utf8")

    @staticmethod
    def config_from_string_dump(dump: str) -> "ProjectConfig":
        return pickle.loads(dump.encode(encoding="utf8"))

    @staticmethod
    def default_config():
        return ProjectConfig(project_title=ProjectConfig.DEFAULT_PROJECT_TITLE)


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

        try:
            config_content = toml.load(path_to_config)
        except toml.decoder.TomlDecodeError as exception:
            print(
                f"warning: could not parse the config file {path_to_config}: "
                f"{exception}."
            )
            print("warning: using default StrictDoc configuration.")
            return ProjectConfig.default_config()
        except Exception as exception:
            raise NotImplementedError from exception

        if "project" in config_content:
            project_content = config_content["project"]
            project_title = project_content.get("title", project_title)
        return ProjectConfig(project_title=project_title)
