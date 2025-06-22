# https://stackoverflow.com/questions/21778252/how-to-raise-an-exception-in-a-jinja2-macro
from typing import Any, List, Optional, Union

from jinja2 import Environment, TemplateRuntimeError, nodes
from jinja2.ext import Extension
from jinja2.parser import Parser


class AssertExtension(Extension):
    tags = {"assert"}

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self.current_line: int = -1
        self.current_file: Optional[str] = None

    def parse(self, parser: Parser) -> Union[nodes.Node, List[nodes.Node]]:
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
        self,
        condition: bool,
        context_or_none: Optional[Any],
        caller: Any,  # noqa: ARG002
    ) -> str:
        if not condition:
            error_message = (
                f"Assertion error in the Jinja template: "
                f"{self.current_file}:{self.current_line}."
            )
            if context_or_none:
                error_message += f" Message: {context_or_none}"
            raise TemplateRuntimeError(error_message)
        return ""
