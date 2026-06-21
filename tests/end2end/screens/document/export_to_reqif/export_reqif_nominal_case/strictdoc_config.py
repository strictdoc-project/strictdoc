from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=["REQIF"],
        exclude_doc_paths=["export.expected.reqif"],
    )
    return config
