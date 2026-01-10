from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="StrictDoc Documentation",
        project_features=[
            # Intentionally nothing.
        ],
        grammars={
            "@my_grammar": "./nested/subnested_grammar/grammar.sgra",
        },
    )
    return config
