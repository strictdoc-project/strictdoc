from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Untitled Project",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "TRACEABILITY_MATRIX_SCREEN",
            "HTML2PDF",
        ],
    )
    return config
