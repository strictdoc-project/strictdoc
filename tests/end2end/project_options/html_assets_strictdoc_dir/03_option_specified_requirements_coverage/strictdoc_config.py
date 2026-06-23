from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        dir_for_sdoc_assets="assets",
        project_features=["TRACEABILITY_MATRIX_SCREEN"],
    )
    return config
