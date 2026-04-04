from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Hybrid Node E2E Test",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "SOURCE_FILE_LANGUAGE_PARSERS",
        ],
        source_nodes=[
            SourceNodesEntry(path=".", uid="DOC", node_type="REQUIREMENT")
        ],
    )
