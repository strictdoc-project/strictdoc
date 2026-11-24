from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        custom_css_path="custom.css",
        favicon_path="favicon.svg",
    )
    return config
