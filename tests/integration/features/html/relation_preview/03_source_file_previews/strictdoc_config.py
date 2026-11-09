from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Relation previews for source files",
        project_features=[
            "TRACEABILITY_SCREEN",
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
        ],
    )
