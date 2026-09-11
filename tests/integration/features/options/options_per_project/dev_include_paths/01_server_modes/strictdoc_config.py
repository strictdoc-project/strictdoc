from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_features=[],
        include_doc_paths=["/docs/**"],
        exclude_doc_paths=["/developer/**"],
        dev_include_paths=["/developer/test_documents/**"],
    )
