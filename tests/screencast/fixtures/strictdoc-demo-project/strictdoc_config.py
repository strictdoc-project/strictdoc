from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="StrictDoc Demo Project",
        project_features=[
            "TABLE_SCREEN",
            "TRACEABILITY_SCREEN",
            "DEEP_TRACEABILITY_SCREEN",
            "SEARCH",
        ],
        include_doc_paths=[
            "/docs/",
        ],
        exclude_doc_paths=[],
    )
