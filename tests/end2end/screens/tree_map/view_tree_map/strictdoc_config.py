from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Tree map test",
        project_features=["TREE_MAP_SCREEN"],
    )
