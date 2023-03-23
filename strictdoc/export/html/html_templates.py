from typing import Any, Optional

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateRuntimeError,
    nodes,
)
from jinja2.ext import Extension

from strictdoc import environment


# https://stackoverflow.com/questions/21778252/how-to-raise-an-exception-in-a-jinja2-macro  # noqa: E501
class AssertExtension(Extension):
    # This is our keyword(s):
    tags = {"assert"}

    def __init__(self, environment):  # pylint: disable=redefined-outer-name
        super().__init__(environment)
        self.current_line = None
        self.current_file = None

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        self.current_line = lineno
        self.current_file = parser.filename

        condition_node = parser.parse_expression()
        if parser.stream.skip_if("comma"):
            context_node = parser.parse_expression()
        else:
            context_node = nodes.Const(None)

        return nodes.CallBlock(
            self.call_method(
                "_assert", [condition_node, context_node], lineno=lineno
            ),
            [],
            [],
            [],
            lineno=lineno,
        )

    def _assert(
        self, condition: bool, context_or_none: Optional[Any], caller
    ):  # pylint: disable=unused-argument
        if not condition:
            error_message = (
                f"Assertion error in the Jinja template: "
                f"{self.current_file}:{self.current_line}."
            )
            if context_or_none:
                error_message += f" Message: {context_or_none}"
            raise TemplateRuntimeError(error_message)
        return ""


class HTMLTemplates:
    jinja_environment = Environment(
        loader=FileSystemLoader(environment.get_path_to_html_templates()),
        undefined=StrictUndefined,
        extensions=[AssertExtension],
    )
    # TODO: Check if this line is still needed (might be some older workaround).
    jinja_environment.globals.update(isinstance=isinstance)
