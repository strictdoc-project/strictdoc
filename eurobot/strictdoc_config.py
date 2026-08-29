from strictdoc.api import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Eurobot",
        project_features=[
            "TABLE_SCREEN",
            "TRACEABILITY_SCREEN",
            "DEEP_TRACEABILITY_SCREEN",
            "TRACEABILITY_MATRIX_SCREEN",
            "SEARCH",
        ],
        grammars={
            "@eurobot": "eurobot_grammar.sgra",
        },
        section_behavior="[[SECTION]]",
    )
    return config
