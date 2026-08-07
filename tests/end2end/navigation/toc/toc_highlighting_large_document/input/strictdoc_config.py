from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="TOC Highlighting Large Document Test",
        chunked_documents_threshold=1000,
    )
