from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        reqif_multiline_is_xhtml=True,
    )
    return config
