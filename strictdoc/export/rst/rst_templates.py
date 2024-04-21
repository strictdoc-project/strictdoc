# mypy: disable-error-code="attr-defined,no-untyped-call,no-untyped-def"
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from strictdoc import environment


class RSTTemplates:
    jinja_environment = Environment(
        loader=FileSystemLoader(environment.get_path_to_rst_templates()),
        undefined=StrictUndefined,
    )
    # TODO: Check if this line is still needed (might be some older workaround).
    jinja_environment.globals.update(isinstance=isinstance)
    jinja_environment.trim_blocks = False
    jinja_environment.lstrip_blocks = False
    jinja_environment.strip_trailing_newlines = False
