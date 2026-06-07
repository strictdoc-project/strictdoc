from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        grammars={
            "@requirements": "requirements.gra.md",
        },
    )
    return config
