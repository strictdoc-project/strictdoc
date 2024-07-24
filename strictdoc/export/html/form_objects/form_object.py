# mypy: disable-error-code="no-untyped-def,union-attr,type-arg"
from dataclasses import dataclass
from typing import Any, Dict, List

from strictdoc.export.html.html_templates import JinjaEnvironment


@dataclass
class RowWithReservedFieldFormObject:
    field: Any
    errors: Dict[str, List]
    jinja_environment: JinjaEnvironment

    def __post_init__(self):
        assert isinstance(
            self.jinja_environment, JinjaEnvironment
        ), self.jinja_environment

    def render(self):
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form_element/row_with_reserved_field/index.jinja",
            form_object=self,
        )
        return rendered_template

    def get_errors(self, field_name) -> List:
        return self.errors.get(field_name, [])


@dataclass
class RowWithCustomFieldFormObject:
    field: Any
    errors: Dict[str, List]
    jinja_environment: JinjaEnvironment

    def __post_init__(self):
        assert self.field is not None
        assert isinstance(
            self.jinja_environment, JinjaEnvironment
        ), self.jinja_environment

    def render(self):
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form_element/row_with_custom_field/index.jinja",
            form_object=self,
        )
        return rendered_template

    def get_errors(self, field_name) -> List:
        return self.errors.get(field_name, [])


@dataclass
class RowWithRelationFormObject:
    relation: Any
    errors: Dict[str, List]
    jinja_environment: JinjaEnvironment

    def __post_init__(self):
        assert self.relation is not None
        assert isinstance(
            self.jinja_environment, JinjaEnvironment
        ), self.jinja_environment

    def render(self):
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form_element/row_with_relation/index.jinja",
            form_object=self,
        )
        return rendered_template

    def get_errors(self, field_name) -> List:
        return self.errors.get(field_name, [])
