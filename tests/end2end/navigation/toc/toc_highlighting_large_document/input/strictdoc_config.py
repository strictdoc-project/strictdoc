from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="TOC Highlighting Large Document Test",
        lazy_document_loading_threshold=1000,
    )
