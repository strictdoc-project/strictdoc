from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_features=[
            "ALL_FEATURES",
            "SEARCH",
        ],
        lazy_document_loading_threshold=100,
        html2pdf_strict=False,
        reqif_multiline_is_xhtml=False,
        reqif_enable_mid=False,
    )
