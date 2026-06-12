from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Lazy Loading Test",
        chunked_documents_threshold=10,
    )
    return config
