from typing import Dict, List, Optional, Set, Tuple, Union

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import Document
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
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.form_data import parse_form_data
from strictdoc.server.error_object import ErrorObject


def is_reserved_field(field_name: str):
    return field_name in (
        RequirementFieldName.UID,
        RequirementFieldName.REFS,
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
        field_required: bool,
        reserved: bool,
    ):
        self.field_mid: str = field_mid
        self.field_name: str = field_name
        self.field_required: bool = field_required
        self.reserved: bool = reserved

    @staticmethod
    def create_from_grammar_field(*, grammar_field: GrammarElementField):
        reserved = is_reserved_field(grammar_field.title)
        return GrammarFormField(
            field_mid=grammar_field.mid,
            field_name=grammar_field.title,
            field_required=grammar_field.required,
            reserved=reserved,
        )

    def get_input_field_name(self):
        return f"document_grammar_field[{self.field_mid}][field_name]"


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
class DocumentGrammarFormObject(ErrorObject):
    def __init__(
        self,
        *,
        document_mid: str,
        fields: List[GrammarFormField],
        relations: List[GrammarFormRelation],
    ):
        assert isinstance(document_mid, str), document_mid
        super().__init__()
        self.document_mid = document_mid
        self.fields: List[GrammarFormField] = fields
        self.relations: List[GrammarFormRelation] = relations

    @staticmethod
    def create_from_request(
        *, document_mid: str, request_form_data: FormData
    ) -> "DocumentGrammarFormObject":
        form_object_fields: List[GrammarFormField] = []
        form_object_relations: List[GrammarFormRelation] = []
        request_form_data_as_list = [
            (field_name, field_value)
            for field_name, field_value in request_form_data.multi_items()
        ]
        request_form_dict: Dict = assert_cast(
            parse_form_data(request_form_data_as_list), dict
        )

        # Grammar fields.
        document_grammar_fields = request_form_dict["document_grammar_field"]
        for field_mid, field_dict in document_grammar_fields.items():
            field_name = field_dict["field_name"]
            form_object_field = GrammarFormField(
                field_mid=field_mid,
                field_name=field_name,
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
            field_role = field_dict["role"]
            form_object_relation = GrammarFormRelation(
                relation_mid=field_mid,
                relation_type=field_type,
                relation_role=field_role,
            )
            form_object_relations.append(form_object_relation)

        form_object = DocumentGrammarFormObject(
            document_mid=document_mid,
            fields=form_object_fields,
            relations=form_object_relations,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *,
        document: Document,
    ) -> "DocumentGrammarFormObject":
        assert isinstance(document, Document)
        assert isinstance(document.grammar, DocumentGrammar)

        grammar: DocumentGrammar = document.grammar
        element: GrammarElement = grammar.elements_by_type["REQUIREMENT"]

        grammar_form_fields: List[GrammarFormField] = []
        for grammar_field in element.fields:
            if grammar_field.title == "REFS":
                continue
            grammar_form_field = GrammarFormField.create_from_grammar_field(
                grammar_field=grammar_field
            )
            grammar_form_fields.append(grammar_form_field)

        grammar_form_relations: List[GrammarFormRelation] = []
        for grammar_relation in element.relations:
            # FIXME: One day enable this.
            if grammar_relation.relation_type == "File":
                continue
            grammar_form_relation = GrammarFormRelation(
                relation_mid=grammar_relation.mid,
                relation_type=grammar_relation.relation_type,
                relation_role=grammar_relation.relation_role,
            )
            grammar_form_relations.append(grammar_form_relation)

        return DocumentGrammarFormObject(
            document_mid=document.reserved_mid,
            fields=grammar_form_fields,
            relations=grammar_form_relations,
        )

    def validate(self) -> bool:
        fields_so_far: Set[str] = set()
        for field in self.fields:
            if len(field.field_name) == 0:
                self.add_error(
                    field.field_name,
                    f"Grammar field {field.field_name} must not be empty.",
                )
                continue

            if field.field_name in fields_so_far:
                self.add_error(
                    field.field_name,
                    f"Grammar field {field.field_name} is not unique.",
                )
            else:
                fields_so_far.add(field.field_name)

        if len(self.relations) == 0:
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
                            relation.relation_mid,
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
                            relation.relation_mid,
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

    def convert_to_document_grammar(self) -> DocumentGrammar:
        grammar_fields: List[GrammarElementField] = []
        for field in self.fields:
            grammar_field = GrammarElementFieldString(
                parent=None,
                title=field.field_name,
                human_title=None,
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
        requirement_element = GrammarElement(
            parent=None,
            tag="REQUIREMENT",
            fields=grammar_fields,
            relations=relation_fields,
        )
        elements: List[GrammarElement] = [requirement_element]
        grammar = DocumentGrammar(parent=None, elements=elements)
        grammar.is_default = False
        return grammar
