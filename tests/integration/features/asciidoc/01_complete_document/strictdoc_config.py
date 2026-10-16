from strictdoc.backend.asciidoc.asciidoc_format import AsciiDocFormat
from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    formats = [
        format_
        for format_ in ProjectConfig.default_formats()
        if "asciidoc" not in format_.handles()
    ]
    return ProjectConfig(formats=[*formats, AsciiDocFormat()])
