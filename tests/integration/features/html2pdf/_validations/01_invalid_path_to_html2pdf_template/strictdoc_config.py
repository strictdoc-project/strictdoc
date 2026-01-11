from strictdoc.core.project_config import ProjectConfig, ProjectFeature


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            ProjectFeature.HTML2PDF
        ],
        html2pdf_template="DOES_NOT_EXIST",
    )
    return config
