from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=["REQUIREMENT_TO_SOURCE_TRACEABILITY"],
        exclude_source_paths=["test.itest"],
        source_nodes=[
            SourceNodesEntry(
                path="src/",
                uid="SRC-NODES-BASE",
                node_type="REQUIREMENT",
            ),
        ],
    )
    return config
