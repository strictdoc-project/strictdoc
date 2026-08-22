from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Deep Link Parent Without Title Test",
        lazy_document_loading_threshold=10,
    )
    return config
