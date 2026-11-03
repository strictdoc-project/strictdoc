from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_features=["REQUIREMENT_TO_SOURCE_TRACEABILITY"],
        include_source_paths=[
            "source.txt", "missing_only.txt", "file.py", "api.h", "api.cpp"
        ],
        relaxed_mode=True,
    )
