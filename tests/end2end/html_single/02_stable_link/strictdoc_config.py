from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Single file test",
        project_features=["STATIC_EDITING"],
    )
