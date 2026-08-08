from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=["REQUIREMENT_TO_SOURCE_TRACEABILITY"],
        include_source_paths=["tests/**.cpp"],
        source_nodes=[
            SourceNodesEntry(
                path="tests/mediated/",
                uid="TEST_DOCUMENT",
                node_type="TEST_CASE",
            )
        ],
    )
    return config
