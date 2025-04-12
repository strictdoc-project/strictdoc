from dataclasses import dataclass
from typing import Any, Dict, List

from markupsafe import Markup

from strictdoc.export.html.html_templates import JinjaEnvironment


@dataclass
class RowWithReservedFieldFormObject:
    field: Any
    errors: Dict[str, List[str]]
    jinja_environment: JinjaEnvironment

    def __post_init__(self) -> None:
        assert isinstance(self.jinja_environment, JinjaEnvironment), (
            self.jinja_environment
        )

    def render(self) -> Markup:
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form_element/row_with_reserved_field/index.jinja",
            form_object=self,
        )
        return rendered_template

    def get_errors(self, field_name: str) -> List[str]:
        return self.errors.get(field_name, [])


@dataclass
class RowWithCustomFieldFormObject:
    field: Any
    errors: Dict[str, List[str]]
    jinja_environment: JinjaEnvironment

    def __post_init__(self) -> None:
        assert self.field is not None
        assert isinstance(self.jinja_environment, JinjaEnvironment), (
            self.jinja_environment
        )

    def render(self) -> Markup:
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form_element/row_with_custom_field/index.jinja",
            form_object=self,
        )
        return rendered_template

    def get_errors(self, field_name: str) -> List[str]:
        return self.errors.get(field_name, [])


@dataclass
class RowWithRelationFormObject:
    relation: Any
    errors: Dict[str, List[str]]
    jinja_environment: JinjaEnvironment

    def __post_init__(self) -> None:
        assert self.relation is not None
        assert isinstance(self.jinja_environment, JinjaEnvironment), (
            self.jinja_environment
        )

    def render(self) -> Markup:
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form_element/row_with_relation/index.jinja",
            form_object=self,
        )
        return rendered_template

    def get_errors(self, field_name: str) -> List[str]:
        return self.errors.get(field_name, [])
