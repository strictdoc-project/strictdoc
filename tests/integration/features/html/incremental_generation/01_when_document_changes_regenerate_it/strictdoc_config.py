from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="StrictDoc Documentation",
        project_features=["TREE_MAP_SCREEN"],
    )
    return config
