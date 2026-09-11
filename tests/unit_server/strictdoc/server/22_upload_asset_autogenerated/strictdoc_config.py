from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "SOURCE_FILE_LANGUAGE_PARSERS",
        ],
        source_nodes=[
            SourceNodesEntry(
                path="src/",
                uid="SRC-NODES-BASE",
                node_type="REQUIREMENT",
            )
        ],
    )
