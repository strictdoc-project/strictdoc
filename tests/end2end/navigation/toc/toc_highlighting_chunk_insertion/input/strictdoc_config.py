from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="TOC Highlighting Chunk Insertion Test",
        chunked_documents_threshold=100,
    )
