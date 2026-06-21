from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[],
        exclude_doc_paths=["docs3/**"],
    )
    return config
