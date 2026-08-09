from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Test project",
        project_features=["SPECIFICATION_GRAPH_SCREEN"],
    )
    return config
