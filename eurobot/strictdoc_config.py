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
            "PROJECT_STATISTICS_SCREEN",
            EurobotTestDashboardFeature(),
        ],
        grammars={
            # Full grammar with every element type. Nothing in this project
            # imports it anymore (each document below has its own narrower
            # grammar so its "Add node" menu only offers the types that make
            # sense for it) - kept registered because the eurobot_grammar and
            # eurobot_rules_import integration tests copy this file/config
            # verbatim and rely on the alias to resolve.
            "@eurobot": "eurobot_grammar.sgra",
            # One grammar file per document, each holding only the element
            # types that document should allow adding: SECTION/TEXT are
            # structural and shared by all three, plus the tag(s) specific
            # to that document.
            "@eurobot_rules": "eurobot_rules_grammar.sgra",
            "@eurobot_requirements": "eurobot_requirements_grammar.sgra",
            "@eurobot_tests": "eurobot_tests_grammar.sgra",
        },
        section_behavior="[[SECTION]]",
        # README.md is a real source file (kept for reference), but it
        # shouldn't be auto-discovered and rendered as a document/nav entry
        # alongside the course's actual RULE/REQUIREMENT/TEST_CASE docs.
        exclude_doc_paths=["/README.md"],
    )
    return config
