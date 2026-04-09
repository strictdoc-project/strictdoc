from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="UPDATED TITLE",
        project_features=[],
    )
    return config
