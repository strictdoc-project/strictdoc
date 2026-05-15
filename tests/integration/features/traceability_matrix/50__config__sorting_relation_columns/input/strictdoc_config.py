from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "TRACEABILITY_MATRIX_SCREEN",
        ],
        exclude_source_paths=[
            "**.itest",
        ],
        traceability_matrix_relation_columns=[
            ("Parent", None),
            ("Parent", "Refines"),
            ("Parent", "REQUIREMENT_FOR"),
            ("File", None),
        ],
    )
    return config
