from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        plantuml_server_url="https://www.plantuml.com/plantuml",
    )
    return config
