# mypy: disable-error-code="arg-type,no-any-return,no-untyped-call,no-untyped-def,union-attr,type-arg"
from typing import Dict, List, Optional, Set, Tuple, Union

from jinja2 import Template
from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementField,
    GrammarElementFieldString,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    GrammarElementRelationParent,
    RequirementFieldName,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.form_objects.form_object import (
    RowWithCustomFieldFormObject,
    RowWithRelationFormObject,
    RowWithReservedFieldFormObject,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.form_data import parse_form_data
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import is_uppercase_underscore_string
from strictdoc.server.error_object import ErrorObject
from strictdoc.server.helpers.turbo import render_turbo_stream


def is_reserved_field(field_name: str):
    return field_name in (
        RequirementFieldName.UID,
        RequirementFieldName.TITLE,
        RequirementFieldName.STATEMENT,
        RequirementFieldName.RATIONALE,
        RequirementFieldName.COMMENT,
    )


@auto_described
class GrammarFormField:
    def __init__(
        self,
        field_mid: str,
        field_name: str,
        field_human_title: Optional[str],
        field_required: bool,
        reserved: bool,
    ):
        self.field_mid: str = field_mid
        self.field_name: str = field_name
        self.field_human_title: Optional[str] = field_human_title
        self.field_required: bool = field_required
        self.reserved: bool = reserved

    @staticmethod
    def create_from_grammar_field(*, grammar_field: GrammarElementField):
        reserved = is_reserved_field(grammar_field.title)
        return GrammarFormField(
            field_mid=grammar_field.mid,
            field_name=grammar_field.title,
            field_human_title=grammar_field.human_title,
            field_required=grammar_field.required,
            reserved=reserved,
        )

    def get_input_field_name(self):
        return f"document_grammar_field[{self.field_mid}][field_name]"

    def get_input_field_human_title(self):
        return f"document_grammar_field[{self.field_mid}][field_human_title]"


@auto_described
class GrammarFormRelation:
    def __init__(
        self,
        relation_mid: str,
        relation_type: str,
        relation_role: Optional[str],
    ):
        self.relation_mid: str = relation_mid
        self.relation_type: str = relation_type
        self.relation_role: str = (
            relation_role if relation_role is not None else ""
        )

    def relation_type_input_name(self):
        return f"document_grammar_relation[{self.relation_mid}][type]"

    def relation_role_input_name(self):
        return f"document_grammar_relation[{self.relation_mid}][role]"


@auto_described
class GrammarElementFormObject(ErrorObject):
    def __init__(
        self,
        *,
        document_mid: str,
        element_mid: str,
        element_name: str,
        fields: List[GrammarFormField],
        relations: List[GrammarFormRelation],
        project_config: ProjectConfig,
        jinja_environment: JinjaEnvironment,
    ):
        assert isinstance(document_mid, str), document_mid
        super().__init__()
        self.document_mid = document_mid
        self.element_mid: str = element_mid
        self.element_name: str = element_name
        self.fields: List[GrammarFormField] = fields
        self.relations: List[GrammarFormRelation] = relations
        self.project_config: ProjectConfig = project_config
        self.jinja_environment: JinjaEnvironment = jinja_environment

    @staticmethod
    def create_from_request(
        *,
        document: SDocDocument,
        request_form_data: FormData,
        project_config: ProjectConfig,
        jinja_environment: JinjaEnvironment,
    ) -> "GrammarElementFormObject":
        form_object_fields: List[GrammarFormField] = []
        form_object_relations: List[GrammarFormRelation] = []
        request_form_data_as_list = [
            (field_name, field_value)
            for field_name, field_value in request_form_data.multi_items()
        ]
        request_form_dict: Dict = assert_cast(
            parse_form_data(request_form_data_as_list), dict
        )

        element_mid = request_form_dict["element_mid"]

        # Grammar fields.
        document_grammar_fields = request_form_dict["document_grammar_field"]
        for field_mid, field_dict in document_grammar_fields.items():
            field_name = field_dict["field_name"]
            field_human_title = field_dict.get("field_human_title")
            if field_human_title is not None:
                field_human_title = field_human_title.strip()
                if len(field_human_title) == 0:
                    field_human_title = None
            form_object_field = GrammarFormField(
                field_mid=field_mid,
                field_name=field_name,
                field_human_title=field_human_title,
                field_required=False,
                reserved=is_reserved_field(field_name),
            )
            form_object_fields.append(form_object_field)

        # Grammar relations.
        document_grammar_relations = request_form_dict.get(
            "document_grammar_relation", {}
        )
        for field_mid, field_dict in document_grammar_relations.items():
            field_type = field_dict["type"]
            field_role = field_dict["role"].strip()
            form_object_relation = GrammarFormRelation(
                relation_mid=field_mid,
                relation_type=field_type,
                relation_role=field_role,
            )
            form_object_relations.append(form_object_relation)

        element: GrammarElement = document.grammar.get_element_by_mid(
            element_mid
        )

        form_object = GrammarElementFormObject(
            document_mid=document.reserved_mid,
            element_mid=element_mid,
            element_name=element.tag,
            fields=form_object_fields,
            relations=form_object_relations,
            project_config=project_config,
            jinja_environment=jinja_environment,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *,
        document: SDocDocument,
        element_mid: str,
        project_config: ProjectConfig,
        jinja_environment: JinjaEnvironment,
    ) -> "GrammarElementFormObject":
        assert isinstance(document, SDocDocument)
        assert isinstance(document.grammar, DocumentGrammar)

        grammar: DocumentGrammar = document.grammar

        element: GrammarElement = grammar.get_element_by_mid(element_mid)

        grammar_form_fields: List[GrammarFormField] = []
        for grammar_field in element.fields:
            grammar_form_field = GrammarFormField.create_from_grammar_field(
                grammar_field=grammar_field
            )
            grammar_form_fields.append(grammar_form_field)

        grammar_form_relations: List[GrammarFormRelation] = []
        for grammar_relation in element.relations:
            grammar_form_relation = GrammarFormRelation(
                relation_mid=grammar_relation.mid,
                relation_type=grammar_relation.relation_type,
                relation_role=grammar_relation.relation_role,
            )
            grammar_form_relations.append(grammar_form_relation)

        return GrammarElementFormObject(
            document_mid=document.reserved_mid,
            element_mid=element_mid,
            element_name=element.tag,
            fields=grammar_form_fields,
            relations=grammar_form_relations,
            project_config=project_config,
            jinja_environment=jinja_environment,
        )

    def validate(self) -> bool:
        fields_so_far: Set[str] = set()
        for field in self.fields:
            if len(field.field_name) == 0:
                self.add_error(
                    field.get_input_field_name(),
                    f"Grammar field {field.field_name} must not be empty.",
                )
                continue

            if not is_uppercase_underscore_string(field.field_name):
                self.add_error(
                    field.get_input_field_name(),
                    (
                        "Grammar field title shall consist of "
                        "uppercase letters, digits and single underscores."
                    ),
                )
                continue

            if field.field_name in fields_so_far:
                self.add_error(
                    field.get_input_field_name(),
                    f"Grammar field {field.field_name} is not unique.",
                )
            else:
                fields_so_far.add(field.field_name)

        if len(self.relations) == 0 and self.element_name != "TEXT":
            self.add_error(
                "Relations_Row",
                (
                    "Every grammar must include at least one relation. "
                    "A grammar lacking any relations is not considered a "
                    "realistic use case. To address this issue, you can create "
                    "a default 'Parent' relation with no assigned role."
                ),
            )
        else:
            general_relations_so_far: Set[str] = set()
            role_relations_so_far: Set[Tuple[str, str]] = set()
            for relation in self.relations:
                if (
                    relation.relation_role is None
                    or len(relation.relation_role) == 0
                ):
                    if relation.relation_type in general_relations_so_far:
                        self.add_error(
                            relation.relation_type_input_name(),
                            (
                                f"A duplicated general relation: {relation.relation_type}. "
                                "A relation is general when it does not have a role that specializes the relation. "
                                "A grammar must have zero or one general relations of a given type (e.g., Parent or Child)."
                            ),
                        )
                    else:
                        general_relations_so_far.add(relation.relation_type)
                else:
                    if (
                        relation.relation_type,
                        relation.relation_role,
                    ) in role_relations_so_far:
                        self.add_error(
                            relation.relation_type_input_name(),
                            (
                                f"A duplicated relation and role: "
                                f"{relation.relation_type} ({relation.relation_role}). "
                                "A grammar must have zero or one relations with a given type and a given role."
                            ),
                        )
                    else:
                        role_relations_so_far.add(
                            (relation.relation_type, relation.relation_role)
                        )

        return len(self.errors) == 0

    def convert_to_grammar_element(
        self, existing_grammar: DocumentGrammar
    ) -> GrammarElement:
        grammar_fields: List[GrammarElementField] = []
        for field in self.fields:
            grammar_field = GrammarElementFieldString(
                parent=None,
                title=field.field_name,
                human_title=field.field_human_title,
                required="True" if field.field_required else "False",
            )
            grammar_fields.append(grammar_field)
        relation_fields: List[
            Union[
                GrammarElementRelationParent,
                GrammarElementRelationChild,
                GrammarElementRelationFile,
            ]
        ] = []

        for relation in self.relations:
            if relation.relation_type == "Parent":
                relation_fields.append(
                    GrammarElementRelationParent(
                        parent=None,
                        relation_type=relation.relation_type,
                        relation_role=relation.relation_role,
                    )
                )
            elif relation.relation_type == "Child":
                relation_fields.append(
                    GrammarElementRelationChild(
                        parent=None,
                        relation_type=relation.relation_type,
                        relation_role=relation.relation_role,
                    )
                )
            elif relation.relation_type == "File":
                relation_fields.append(
                    GrammarElementRelationFile(
                        parent=None,
                        relation_type=relation.relation_type,
                    )
                )
            else:
                raise NotImplementedError(relation)

        existing_element = existing_grammar.get_element_by_mid(self.element_mid)
        requirement_element = GrammarElement(
            parent=None,
            tag=existing_element.tag,
            fields=grammar_fields,
            relations=relation_fields,
        )
        return requirement_element

    def render(self):
        template: Template = self.jinja_environment.get_template(
            "components/grammar_form_element/index.jinja"
        )
        rendered_template = template.render(form_object=self)
        return render_turbo_stream(
            content=rendered_template, action="update", target="modal"
        )

    def render_after_validation(self):
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/grammar_form_element/index.jinja", form_object=self
        )
        return render_turbo_stream(
            content=rendered_template, action="update", target="modal"
        )

    def render_row_with_reserved_field(self, field: GrammarFormField) -> str:
        form_object = RowWithReservedFieldFormObject(
            field=field,
            errors=self.errors,
            jinja_environment=self.jinja_environment,
        )
        return form_object.render()

    def render_row_with_custom_field(self, field: GrammarFormField) -> str:
        assert isinstance(field, GrammarFormField)
        form_object = RowWithCustomFieldFormObject(
            field=field,
            errors=self.errors,
            jinja_environment=self.jinja_environment,
        )
        return form_object.render()

    def render_row_with_relation(self, relation: GrammarFormRelation) -> str:
        assert isinstance(relation, GrammarFormRelation)
        form_object = RowWithRelationFormObject(
            relation=relation,
            errors=self.errors,
            jinja_environment=self.jinja_environment,
        )
        return form_object.render()

    def render_row_with_new_field(self) -> str:
        field: GrammarFormField = GrammarFormField(
            field_mid=MID.create(),
            field_name="",
            field_human_title=None,
            field_required=False,
            reserved=False,
        )
        form_object = RowWithCustomFieldFormObject(
            field=field,
            errors=self.errors,
            jinja_environment=self.jinja_environment,
        )
        rendered_template: str = form_object.render()
        return render_turbo_stream(
            content=rendered_template,
            action="append",
            target="document__editable_grammar_fields",
        )

    def render_row_with_new_relation(self) -> str:
        relation = GrammarFormRelation(
            relation_mid=MID.create(),
            relation_type="Parent",
            relation_role="",
        )
        form_object = RowWithRelationFormObject(
            relation=relation,
            errors=self.errors,
            jinja_environment=self.jinja_environment,
        )
        rendered_template: str = form_object.render()
        return render_turbo_stream(
            content=rendered_template,
            action="append",
            target="document__editable_grammar_relations",
        )

    @staticmethod
    def render_close_form() -> str:
        return render_turbo_stream(
            content="",
            action="update",
            target="modal",
        )
