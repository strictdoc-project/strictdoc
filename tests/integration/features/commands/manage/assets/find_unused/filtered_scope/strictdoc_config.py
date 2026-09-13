from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_features=[],
        include_doc_paths=["included/**", "tests/**"],
        exclude_doc_paths=["included/excluded/**"],
    )
