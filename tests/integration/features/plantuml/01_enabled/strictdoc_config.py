from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "TABLE_SCREEN",
            "TRACEABILITY_SCREEN",
            "DEEP_TRACEABILITY_SCREEN",
        ],
        plantuml_server_url="https://www.plantuml.com/plantuml",
    )
    return config
