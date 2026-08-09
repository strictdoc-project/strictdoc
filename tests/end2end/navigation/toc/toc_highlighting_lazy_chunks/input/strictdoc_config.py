from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="TOC Highlighting Lazy Chunks Test",
        lazy_document_loading_threshold=10,
    )
    return config
