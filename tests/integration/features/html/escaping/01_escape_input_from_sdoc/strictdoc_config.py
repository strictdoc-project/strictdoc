from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "DEEP_TRACEABILITY_SCREEN",
            "TABLE_SCREEN",
            "TRACEABILITY_SCREEN",
            "TRACEABILITY_MATRIX_SCREEN",
        ],
    )
    return config
