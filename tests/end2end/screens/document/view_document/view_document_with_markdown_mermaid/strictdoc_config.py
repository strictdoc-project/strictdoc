from strictdoc.core.project_config import ProjectConfig, ProjectFeature


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            ProjectFeature.MERMAID,
        ],
    )
    return config
