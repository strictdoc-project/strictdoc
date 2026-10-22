from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "TRACEABILITY_MATRIX_SCREEN",
        ],
        exclude_source_paths=[
            "**.itest",
        ],
    )
    return config
