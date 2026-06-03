from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
        ],
        source_root_path="..",
        include_doc_paths=[],
        include_source_paths=[
            "/tests",
        ],
    )
    return config
