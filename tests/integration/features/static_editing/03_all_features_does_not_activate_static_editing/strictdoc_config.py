from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Static editing test",
        project_features=["ALL_FEATURES"],
    )
