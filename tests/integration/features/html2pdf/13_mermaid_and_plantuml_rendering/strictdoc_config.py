from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        dir_for_sdoc_cache="./Output/cache",
        project_features=["HTML2PDF"],
    )
    return config
