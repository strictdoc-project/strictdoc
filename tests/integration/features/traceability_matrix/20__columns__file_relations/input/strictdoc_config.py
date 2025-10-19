import os.path

from strictdoc.core.project_config import ProjectConfig

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "TRACEABILITY_MATRIX_SCREEN",
        ],
        exclude_source_paths=[
            "**.itest",
        ],
        source_root_path=parent_dir,
    )
    return config
