from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
        ],
        exclude_source_paths = [
            "test.itest",
        ],
    )
    return config
