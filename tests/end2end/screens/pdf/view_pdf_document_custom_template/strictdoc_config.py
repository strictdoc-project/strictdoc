from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=["HTML2PDF"],
        html2pdf_template="html2pdf_template/index.jinja",
    )
    return config
