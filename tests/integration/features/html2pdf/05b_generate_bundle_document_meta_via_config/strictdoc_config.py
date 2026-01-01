from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=[
            "HTML2PDF",
        ],
        bundle_document_uid="MY_BUNDLE_DOC_UID",
        bundle_document_version="v1.2.3",
        bundle_document_date="2026-01-01"
    )
    return config
