from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "HTML2PDF",
        ],
        html2pdf_forced_page_break_nodes=[
            "REQUIREMENT"
        ]
    )
    return config
