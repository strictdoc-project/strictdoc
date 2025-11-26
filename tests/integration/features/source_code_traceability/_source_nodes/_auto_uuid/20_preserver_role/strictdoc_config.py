from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Linux",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "SOURCE_FILE_LANGUAGE_PARSERS",
        ],
        source_nodes=[
            SourceNodesEntry(
                path="src/",
                uid="DOC-1",
                node_type="REQUIREMENT",
            ),
        ],
    )
    return config
