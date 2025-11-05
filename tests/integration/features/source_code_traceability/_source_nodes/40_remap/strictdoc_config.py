from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="StrictDoc Documentation",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "SOURCE_FILE_LANGUAGE_PARSERS",
        ],
        source_nodes = [
            SourceNodesEntry(
                path="src/",
                uid="SRC-NODES-BASE",
                node_type="REQUIREMENT",
                sdoc_to_source_map={
                    "UID": "THEIR_ID",
                    "TITLE": "THEIR_TITLE",
                    "MY_FOO": "THEIR_FOO"
                }
            )
        ],
        exclude_source_paths = [
            "test.itest"
        ]
    )
    return config
