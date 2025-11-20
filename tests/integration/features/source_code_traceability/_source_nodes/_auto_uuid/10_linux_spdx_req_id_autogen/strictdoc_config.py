
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
                uid="SPDX_DOC",
                node_type="REQUIREMENT",
                sdoc_to_source_map={
                    "MID": "SPDX-Req-ID",
                    "STATEMENT": "SPDX-Req-Text",
                }
            ),
        ],
        exclude_source_paths=[
            "*.itest"
        ]
    )
    return config
