# mypy: disable-error-code="no-redef,no-untyped-def,union-attr,type-arg"
from dataclasses import dataclass
from typing import Any, Dict, List

from strictdoc.export.html.html_templates import JinjaEnvironment


@dataclass
class RowWithGrammarElementFormObject:
    field: Any
    errors: Dict[str, List]
    jinja_environment: JinjaEnvironment

    def __post_init__(self):
        assert self.field is not None
        assert isinstance(self.jinja_environment, JinjaEnvironment), (
            self.jinja_environment
        )

    def render(self):
        if self.field.is_new:
            rendered_template = self.jinja_environment.render_template_as_markup(
                "components/grammar_form/row_with_new_grammar_element/index.jinja",
                form_object=self,
            )
            return rendered_template
        else:
            rendered_template = self.jinja_environment.render_template_as_markup(
                "components/grammar_form/row_with_grammar_element/index.jinja",
                form_object=self,
            )
            return rendered_template

    def get_errors(self, field_name) -> List:
        return self.errors.get(field_name, [])
