from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Static editing test",
        project_features=["STATIC_EDITING"],
        # The document has 40 nodes. A threshold of 5 loads the document in
        # chunks of 5 nodes, so the last node is not loaded at the start.
        lazy_document_loading_threshold=5,
    )
