from typing import Dict, List, Set

from jinja2 import Environment, Template
from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.form_objects.rows.row_with_grammar_element_form_object import (
    RowWithGrammarElementFormObject,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.form_data import parse_form_data
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import is_uppercase_underscore_string
from strictdoc.server.error_object import ErrorObject
from strictdoc.server.helpers.turbo import render_turbo_stream


@auto_described
class GrammarElementFormField:
    def __init__(
        self,
        field_mid: str,
        field_name: str,
        document_mid: str,
    ):
        self.field_mid: str = field_mid
        self.field_name: str = field_name
        self.document_mid: str = document_mid

    @staticmethod
    def create(*, grammar_element: GrammarElement, document_mid: str):
        return GrammarElementFormField(
            field_mid=grammar_element.mid,
            field_name=grammar_element.tag,
            document_mid=document_mid,
        )

    def get_input_field_name(self):
        return f"document_grammar_element_field[{self.field_mid}][field_name]"


@auto_described
class GrammarFormObject(ErrorObject):
    def __init__(
        self,
        *,
        document_mid: str,
        fields: List[GrammarElementFormField],
        project_config: ProjectConfig,
        jinja_environment: Environment,
    ):
        assert isinstance(document_mid, str), document_mid
        super().__init__()
        self.document_mid = document_mid
        self.fields: List[GrammarElementFormField] = fields
        self.project_config: ProjectConfig = project_config
        self.jinja_environment: Environment = jinja_environment

    @staticmethod
    def create_from_request(
        *,
        document_mid: str,
        request_form_data: FormData,
        project_config: ProjectConfig,
        jinja_environment: Environment,
    ) -> "GrammarFormObject":
        form_object_fields: List[GrammarElementFormField] = []
        request_form_data_as_list = [
            (field_name, field_value)
            for field_name, field_value in request_form_data.multi_items()
        ]
        request_form_dict: Dict = assert_cast(
            parse_form_data(request_form_data_as_list), dict
        )

        document_grammar_fields = request_form_dict[
            "document_grammar_element_field"
        ]
        for field_mid, field_dict in document_grammar_fields.items():
            field_name = field_dict["field_name"]
            form_object_field = GrammarElementFormField(
                field_mid=field_mid,
                field_name=field_name,
                document_mid=document_mid,
            )
            form_object_fields.append(form_object_field)

        form_object = GrammarFormObject(
            document_mid=document_mid,
            fields=form_object_fields,
            project_config=project_config,
            jinja_environment=jinja_environment,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *,
        document: SDocDocument,
        project_config: ProjectConfig,
        jinja_environment: Environment,
    ) -> "GrammarFormObject":
        assert isinstance(document, SDocDocument)
        assert isinstance(document.grammar, DocumentGrammar)

        grammar: DocumentGrammar = document.grammar

        grammar_element_form_fields: List[GrammarElementFormField] = []

        for element_ in grammar.elements:
            grammar_form_field = GrammarElementFormField.create(
                grammar_element=element_, document_mid=document.reserved_mid
            )
            grammar_element_form_fields.append(grammar_form_field)

        return GrammarFormObject(
            document_mid=document.reserved_mid,
            fields=grammar_element_form_fields,
            project_config=project_config,
            jinja_environment=jinja_environment,
        )

    def validate(self) -> bool:
        fields_so_far: Set[str] = set()
        for field in self.fields:
            if len(field.field_name) == 0:
                self.add_error(
                    field.field_mid,
                    "Provide a name for the grammar element.",
                )
                continue

            if not is_uppercase_underscore_string(field.field_name):
                self.add_error(
                    field.field_mid,
                    (
                        "Grammar element title shall consist of "
                        "uppercase letters, digits and single underscores."
                    ),
                )

            if field.field_name in fields_so_far:
                self.add_error(
                    field.field_mid,
                    f"Grammar element {field.field_name} is not unique.",
                )
            else:
                fields_so_far.add(field.field_name)

        return len(self.errors) == 0

    def render(self):
        template: Template = self.jinja_environment.get_template(
            "components/grammar_form/index.jinja"
        )
        rendered_template = template.render(form_object=self)
        return render_turbo_stream(
            content=rendered_template, action="update", target="modal"
        )

    def render_row_with_grammar_element(
        self, field: GrammarElementFormField, errors
    ) -> str:
        form_object = RowWithGrammarElementFormObject(
            field=field, errors=errors, jinja_environment=self.jinja_environment
        )
        return form_object.render()

    def render_row_with_new_grammar_element(self) -> str:
        field: GrammarElementFormField = GrammarElementFormField(
            field_mid=MID.create(),
            field_name="",
            document_mid=self.document_mid,
        )
        form_object = RowWithGrammarElementFormObject(
            field=field, errors=[], jinja_environment=self.jinja_environment
        )
        rendered_template: str = form_object.render_new()
        return render_turbo_stream(
            content=rendered_template,
            action="append",
            target="document__editable_grammar_elements",
        )

    @staticmethod
    def render_close_form() -> str:
        return render_turbo_stream(
            content="",
            action="update",
            target="modal",
        )