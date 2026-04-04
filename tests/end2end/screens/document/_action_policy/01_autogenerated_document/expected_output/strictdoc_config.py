from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Autogen E2E Test",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "SOURCE_FILE_LANGUAGE_PARSERS",
        ],
    )
    return config
