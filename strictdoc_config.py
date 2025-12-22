from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="StrictDoc Documentation",
        dir_for_sdoc_assets="assets",
        dir_for_sdoc_cache="output/_cache",
        project_features=[
            # Stable features.
            "TABLE_SCREEN",
            "TRACEABILITY_SCREEN",
            "DEEP_TRACEABILITY_SCREEN",
            "SEARCH",
            # Stable features but not used by StrictDoc.
            # "MATHJAX"
            # Experimental features.
            "PROJECT_STATISTICS_SCREEN",
            "TREE_MAP_SCREEN",
            # "REQIF",
            # "STANDALONE_DOCUMENT_SCREEN",
            "TRACEABILITY_MATRIX_SCREEN",
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "SOURCE_FILE_LANGUAGE_PARSERS",
            "HTML2PDF",
            "DIFF",
            "NESTOR",
        ],
        include_doc_paths=[
            "/docs/",
            "/docs_extra/",
            "/reports/",
        ],
        exclude_doc_paths=[
            "/.*/",
            "/docs/sphinx/",
            "/strictdoc/",
            "/tests/",
        ],
        include_source_paths=[
            "/LICENSE",
            "/NOTICE",
            "/.github/workflows/",
            "/strictdoc/**.py",
            "/strictdoc/**.js",
            "/strictdoc/**.jinja.rst",
            "/tests/integration/**itest",
            "/tests/unit/**.py",
            "/tests/unit_server/**.py",
            "/tests/end2end/**.py",
            "/tasks.py",
            "/pyproject.toml",
        ],
        exclude_source_paths=[
            "/developer/",
            # StrictDoc (almost never) uses __init__ files.
            # The used files will be whitelisted include_source_paths.
            "**__init__.py",
            "**.test.py",
            # Uncomment when it is clear what to do with helpers.
            "/strictdoc/helpers/*.py",
            "/tests/unit/strictdoc/helpers/*.py",
            "/tests/unit/*.py",
            "/tests/unit/helpers/*.py",
            "/tests/integration/**ignored.itest",
            "/tests/end2end/*.py",
            "/tests/end2end/helpers/**.py",
        ],
        test_report_root_dict={
            "reports/tests_integration.lit.junit.xml": "tests/integration",
            "reports/tests_integration_html2pdf.lit.junit.xml": "tests/integration",
        },
        # Waiting for a fix to be released soon.
        html2pdf_strict=False,
        reqif_multiline_is_xhtml=True,
        reqif_enable_mid=True,
        section_behavior="[[SECTION]]",
        statistics_generator="docs.sdoc_project_statistics.SDocStatisticsGenerator",
    )
    return config
