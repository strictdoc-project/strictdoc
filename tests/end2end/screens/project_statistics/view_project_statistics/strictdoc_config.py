from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "PROJECT_STATISTICS_SCREEN",
            "SEARCH",
        ],
    )
    return config
