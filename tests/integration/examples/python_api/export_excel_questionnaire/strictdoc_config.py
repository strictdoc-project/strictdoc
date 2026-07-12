from strictdoc.api import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Heavy Duty Vehicle Cybersecurity Requirements (HD VCR)",
        project_features=[],
        include_doc_paths=["*.sdoc"],
    )
    return config
