from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[],
        include_doc_paths=[
            " ",
        ],
    )
    return config
