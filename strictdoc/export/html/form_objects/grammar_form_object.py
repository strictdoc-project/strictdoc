# mypy: disable-error-code="arg-type,no-any-return,no-untyped-call,no-untyped-def,type-arg"
from typing import Dict, List, Optional, Set

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
from strictdoc.export.html.html_templates import JinjaEnvironment
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
        is_new: bool,
        field_mid: str,
        field_name: str,
        document_mid: str,
    ):
        self.is_new: bool = is_new
        self.field_mid: str = field_mid
        self.field_name: str = field_name
        self.document_mid: str = document_mid

    @staticmethod
    def create(
        *,
        is_new: bool,
        grammar_element: GrammarElement,
        document_mid: str,
    ):
        return GrammarElementFormField(
            is_new=is_new,
            field_mid=grammar_element.mid,
            field_name=grammar_element.tag,
            document_mid=document_mid,
        )

    def get_input_field_name(self):
        return f"document_grammar_element_field[{self.field_mid}][field_name]"

    def get_input_field_is_new(self):
        return f"document_grammar_element_field[{self.field_mid}][is_new]"

    def get_is_new_as_string(self):
        return "true" if self.is_new else "false"


@auto_described
class GrammarFormObject(ErrorObject):
    def __init__(
        self,
        *,
        document_mid: str,
        fields: List[GrammarElementFormField],
        project_config: ProjectConfig,
        jinja_environment: JinjaEnvironment,
        imported_grammar_file: Optional[str],
    ):
        assert isinstance(document_mid, str), document_mid
        super().__init__()
        self.document_mid = document_mid
        self.fields: List[GrammarElementFormField] = fields
        self.project_config: ProjectConfig = project_config
        self.jinja_environment: JinjaEnvironment = jinja_environment
        self.imported_grammar_file: Optional[str] = imported_grammar_file

    @staticmethod
    def create_from_request(
        *,
        document_mid: str,
        request_form_data: FormData,
        project_config: ProjectConfig,
        jinja_environment: JinjaEnvironment,
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
            is_new = field_dict["is_new"] == "true"
            field_name = field_dict["field_name"]

            form_object_field = GrammarElementFormField(
                is_new=is_new,
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
            imported_grammar_file=None,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *,
        document: SDocDocument,
        project_config: ProjectConfig,
        jinja_environment: JinjaEnvironment,
    ) -> "GrammarFormObject":
        assert isinstance(document, SDocDocument)
        assert isinstance(document.grammar, DocumentGrammar)

        grammar: DocumentGrammar = document.grammar

        grammar_element_form_fields: List[GrammarElementFormField] = []

        for element_ in grammar.elements:
            grammar_form_field = GrammarElementFormField.create(
                is_new=False,
                grammar_element=element_,
                document_mid=document.reserved_mid,
            )
            grammar_element_form_fields.append(grammar_form_field)

        return GrammarFormObject(
            document_mid=document.reserved_mid,
            fields=grammar_element_form_fields,
            project_config=project_config,
            jinja_environment=jinja_environment,
            imported_grammar_file=grammar.import_from_file,
        )

    def validate(self) -> bool:
        fields_so_far: Set[str] = set()
        for field in self.fields:
            if len(field.field_name) == 0:
                self.add_error(
                    field.get_input_field_name(),
                    "Provide a name for the grammar element.",
                )
                continue

            if not is_uppercase_underscore_string(field.field_name):
                self.add_error(
                    field.get_input_field_name(),
                    (
                        "Grammar element title shall consist of "
                        "uppercase letters, digits and single underscores."
                    ),
                )

            if field.field_name in fields_so_far:
                self.add_error(
                    field.get_input_field_name(),
                    f"Grammar element {field.field_name} is not unique.",
                )
            else:
                fields_so_far.add(field.field_name)

        return len(self.errors) == 0

    def render(self):
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form/index.jinja", form_object=self
        )
        return render_turbo_stream(
            content=rendered_template, action="update", target="modal"
        )

    def render_row_with_grammar_element(
        self, field: GrammarElementFormField
    ) -> str:
        form_object = RowWithGrammarElementFormObject(
            field=field,
            errors=self.errors,
            jinja_environment=self.jinja_environment,
        )
        return form_object.render()

    def render_row_with_new_grammar_element(self) -> str:
        field: GrammarElementFormField = GrammarElementFormField(
            is_new=True,
            field_mid=MID.create(),
            field_name="",
            document_mid=self.document_mid,
        )
        form_object = RowWithGrammarElementFormObject(
            field=field,
            errors=self.errors,
            jinja_environment=self.jinja_environment,
        )
        rendered_template: str = form_object.render()
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
