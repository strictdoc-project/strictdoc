from jinja2 import Environment, StrictUndefined, FileSystemLoader

from strictdoc import environment


class HTMLTemplates:
    jinja_environment = Environment(
        loader=FileSystemLoader(environment.get_path_to_html_templates()),
        undefined=StrictUndefined,
    )
    # TODO: Check if this line is still needed (might be some older workaround).
    jinja_environment.globals.update(isinstance=isinstance)
