from strictdoc.core.project_config import ProjectConfig, ProjectFeature


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY,
        ],
        include_source_paths=[
            "src1/**",
        ],
    )
    return config
