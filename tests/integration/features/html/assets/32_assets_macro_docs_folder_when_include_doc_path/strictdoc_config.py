# strictdoc_config.py
from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Test Project",
        include_doc_paths=["docs/"]
    )
    return config

