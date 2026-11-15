from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Lazy Document Loading (static export, uncompressed)",
        lazy_document_loading_threshold=10,
        lazy_document_loading_compress_chunks=False,
    )
    return config
