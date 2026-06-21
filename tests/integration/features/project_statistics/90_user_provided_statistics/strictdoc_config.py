from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Test project",
        project_features=["PROJECT_STATISTICS_SCREEN"],
        statistics_generator="statistics_generator.CustomStatisticsGenerator",
    )
    return config
