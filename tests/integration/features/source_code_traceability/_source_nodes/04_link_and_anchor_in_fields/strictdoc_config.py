from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
        ],
        source_nodes=[
            SourceNodesEntry(
                path="tests/",
                uid="TEST_DOC",
                node_type="TEST_SPEC",
            )
        ],
        exclude_source_paths=[
            "test.itest"
        ],
    )
    return config
