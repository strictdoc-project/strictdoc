from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        source_root_path="src",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
        ],
    )
    return config
