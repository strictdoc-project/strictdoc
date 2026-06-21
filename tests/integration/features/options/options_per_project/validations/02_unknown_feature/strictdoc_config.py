from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Test Project title read from TOML file",
        project_features=["THIS_FEATURE_DOES_NOT_EXIST"],
    )
    return config
