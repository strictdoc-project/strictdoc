from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        include_doc_paths=["prod_requirements/"],
    )
    return config
