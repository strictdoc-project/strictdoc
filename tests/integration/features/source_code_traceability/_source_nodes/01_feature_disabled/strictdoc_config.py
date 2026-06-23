from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=["REQUIREMENT_TO_SOURCE_TRACEABILITY"],
        exclude_source_paths=["test.itest"],
        source_nodes=[
            SourceNodesEntry(
                path="tests_another_path/",
                uid="TEST_DOC",
                node_type="TEST_SPEC",
            ),
        ],
    )
    return config
