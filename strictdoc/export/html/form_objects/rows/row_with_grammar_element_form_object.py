from dataclasses import dataclass
from typing import Any, List

from jinja2 import Environment, Template


@dataclass
class RowWithGrammarElementFormObject:
    field: Any
    errors: List[str]
    jinja_environment: Environment

    def __post_init__(self):
        assert self.field is not None
        assert isinstance(
            self.jinja_environment, Environment
        ), self.jinja_environment

    def render(self):
        template: Template = self.jinja_environment.get_template(
            "components/grammar_form/row_with_grammar_element/index.jinja"
        )
        rendered_template = template.render(form_object=self)
        return rendered_template

    def render_new(self):
        template: Template = self.jinja_environment.get_template(
            "components/grammar_form/row_with_new_grammar_element/index.jinja"
        )
        rendered_template = template.render(form_object=self)
        return rendered_template
