from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=["REQUIREMENT_TO_SOURCE_TRACEABILITY"],
        include_source_paths=["other_src/*.c"],
        exclude_source_paths=["src.itest"],
        source_nodes=[
            SourceNodesEntry(
                path="src/",
                uid="SRC_DOC",
                node_type="SRC_SPEC",
            ),
        ],
    )
    return config
