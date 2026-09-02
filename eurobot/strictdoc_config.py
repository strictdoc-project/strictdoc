from strictdoc.api import ProjectConfig
from strictdoc.features.eurobot_test_dashboard.feature import (
    EurobotTestDashboardFeature,
)


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Eurobot",
        project_features=[
            "TABLE_SCREEN",
            "TRACEABILITY_SCREEN",
            "DEEP_TRACEABILITY_SCREEN",
            "TRACEABILITY_MATRIX_SCREEN",
            "SEARCH",
            EurobotTestDashboardFeature(),
        ],
        grammars={
            "@eurobot": "eurobot_grammar.sgra",
        },
        section_behavior="[[SECTION]]",
        # README.md is a real source file (kept for reference), but it
        # shouldn't be auto-discovered and rendered as a document/nav entry
        # alongside the course's actual RULE/REQUIREMENT/TEST_CASE docs.
        exclude_doc_paths=["/README.md"],
    )
    return config
