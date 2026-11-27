from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        html_single_libraries="cdn",
        html_single_library_modes={"plantuml": "embed"},
        html_single_fonts="system",
        html_single_cdn_url="https://npm.example.com/npm/",
    )
