from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Relation previews in a chunked document",
        lazy_document_loading_threshold=1,
    )
    return config
