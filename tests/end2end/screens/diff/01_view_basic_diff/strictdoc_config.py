from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        dir_for_sdoc_cache="./output/cache",
        project_features=["DIFF"],
    )
    return config
