from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Relative path little try",
        source_root_path="../src",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
        ],
        include_doc_paths=[
            "**",
        ],
        include_source_paths = [
            "try/**",
        ],
    )
    return config
