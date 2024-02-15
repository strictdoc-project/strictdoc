from textx import TextXSyntaxError

from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
    GrammarElementField,
)
from strictdoc.backend.sdoc.models.document_view import ViewElement
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.reference import Reference


def get_textx_syntax_error_message(exception: TextXSyntaxError):
    return f"SDoc markup error: {exception.context}."


class StrictDocSemanticError(Exception):
    def __init__(
        self, title, hint, example, line=None, col=None, filename=None
    ):
        super().__init__(title, hint, line, col, filename)
        self.title = title
        self.hint = hint
        self.example = example
        self.line = line
        self.col = col
        self.file_path = filename

    @staticmethod
    def unknown_requirement_type(
        requirement_type, line=None, col=None, filename=None
    ):
        return StrictDocSemanticError(
            title=f"Invalid requirement type: {requirement_type}.",
            hint=None,
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def unregistered_field(
        *,
        field_name: str,
        requirement: SDocNode,
        document_grammar: DocumentGrammar,
        line=None,
        col=None,
        filename=None,
    ):
        grammar_dump = document_grammar.dump_fields(
            requirement.requirement_type
        )
        return StrictDocSemanticError(
            title=f"Invalid requirement field: {field_name}",
            hint=(
                f"Compare with the document grammar: [{grammar_dump}] "
                f"for type: {requirement.requirement_type}."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def missing_required_field(
        requirement: SDocNode,
        grammar_field: GrammarElementField,
        document_grammar: DocumentGrammar,
        line=None,
        col=None,
        filename=None,
    ):
        grammar_fields = document_grammar.dump_fields(
            requirement.requirement_type
        )
        return StrictDocSemanticError(
            title=(
                f"Requirement is missing a field that is required by "
                f"grammar: {grammar_field.title}."
            ),
            hint=(
                f"Requirement fields: [{requirement.dump_fields_as_parsed()}], "
                f"grammar fields: [{grammar_fields}]."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def unexpected_field_outside_grammar(
        requirement: SDocNode,
        requirement_field: SDocNodeField,
        document_grammar: DocumentGrammar,
        line=None,
        col=None,
        filename=None,
    ):
        grammar_fields = document_grammar.dump_fields(
            requirement.requirement_type
        )
        return StrictDocSemanticError(
            title=(
                f"Unexpected field outside grammar: "
                f"{requirement_field.field_name}"
            ),
            hint=(
                f"Requirement fields: [{requirement.dump_fields_as_parsed()}], "
                f"grammar fields: [{grammar_fields}]."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def wrong_field_order(
        requirement: SDocNode,
        document_grammar: DocumentGrammar,
        problematic_field: SDocNodeField,
        line=None,
        col=None,
        filename=None,
    ):
        assert isinstance(
            problematic_field, SDocNodeField
        ), f"{problematic_field}"
        requirement_dump = requirement.dump_fields_as_parsed()
        grammar_dump = document_grammar.dump_fields(
            requirement.requirement_type
        )
        return StrictDocSemanticError(
            title=f"Wrong field order for requirement: [{requirement_dump}].",
            hint=(
                f"Problematic field: {problematic_field.field_name}. "
                f"Compare with the document grammar: [{grammar_dump}] "
                f"for type: {requirement.requirement_type}."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def invalid_choice_field(
        requirement: SDocNode,
        document_grammar: DocumentGrammar,
        requirement_field: SDocNodeField,
        line=None,
        col=None,
        filename=None,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field has an invalid SingleChoice value: "
                f"{requirement_field.field_value}."
            ),
            hint=(
                f"Problematic field: {requirement_field.field_name}. "
                f"Compare with the document grammar: "
                f"["
                f"{document_grammar.dump_fields(requirement.requirement_type)}"
                f"] "
                f"for type: {requirement.requirement_type}."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def invalid_multiple_choice_field(
        requirement: SDocNode,
        document_grammar: DocumentGrammar,
        requirement_field: SDocNodeField,
        line=None,
        col=None,
        filename=None,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field has an invalid MultipleChoice value: "
                f"{requirement_field.field_value}."
            ),
            hint=(
                f"Problematic field: {requirement_field.field_name}. "
                f"Compare with the document grammar: "
                f"["
                f"{document_grammar.dump_fields(requirement.requirement_type)}"
                f"] "
                f"for type: {requirement.requirement_type}."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def not_comma_separated_choices(
        requirement_field: SDocNodeField,
        line=None,
        col=None,
        filename=None,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field of type MultipleChoice is invalid: "
                f"{requirement_field.field_value}."
            ),
            hint="MultipleChoice field requires ', '-separated values.",
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def not_comma_separated_tag_field(
        requirement_field: SDocNodeField,
        line=None,
        col=None,
        filename=None,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field of type Tag is invalid: "
                f"{requirement_field.field_value}."
            ),
            hint="Tag field requires ', '-separated values.",
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def invalid_reference_type_item(
        requirement: SDocNode,
        reference_item: Reference,
        line=None,
        col=None,
        filename=None,
    ):
        role_and_type = (
            f"{reference_item.ref_type} / {reference_item.role}"
            if reference_item.role is not None
            else reference_item.ref_type
        )
        return StrictDocSemanticError(
            title=(
                f"Requirement relation type/role is not registered: "
                f"{role_and_type}."
            ),
            hint=(f"Problematic requirement: {requirement.reserved_uid}."),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def grammar_missing_reserved_statement(
        grammar_element: GrammarElement,
        line=None,
        col=None,
        filename=None,
    ):
        return StrictDocSemanticError(
            title=(
                f"Grammar element '{grammar_element.tag}' is missing a reserved"
                " STATEMENT field declaration."
            ),
            hint=(
                "STATEMENT plays a key role in StrictDoc's HTML user interface "
                "as well as in the other export formats. It is a reserved field"
                " that any grammar must provide."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def view_references_nonexisting_grammar_element(
        view_element: ViewElement,
        object_type: str,
        line=None,
        col=None,
        filename=None,
    ):
        return StrictDocSemanticError(
            title=(
                f"View element '{view_element.view_id}' references a non-existing"
                f" grammar element '{object_type}'."
            ),
            hint=(
                "Make sure that each View element references an existing "
                "object in the grammar or the default REQUIREMENT object."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def view_references_nonexisting_field(
        view_element: ViewElement,
        object_type: str,
        field_name: str,
        line=None,
        col=None,
        filename=None,
    ):
        return StrictDocSemanticError(
            title=(
                f"View element '{view_element.view_id}' references a non-existing"
                f" field '{field_name}' for grammar element '{object_type}'."
            ),
            hint=(
                "Make sure that each View element references an existing "
                "field in the grammar for the given grammar element."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def default_view_doesnt_exist(
        default_view: str, line=None, col=None, filename=None
    ):
        return StrictDocSemanticError(
            title=(
                f"Default view '{default_view}' does not exist in the document."
            ),
            hint=(
                "Make sure that the specified default view is created in the "
                "VIEWS configuration."
            ),
            example=None,
            line=line,
            col=col,
            filename=filename,
        )

    def to_print_message(self):
        message = ""
        message += f"error: could not parse file: {self.file_path}.\n"
        message += f"Semantic error: {self.title}\n"
        message += f"Location: {self.file_path}:{self.line}:{self.col}"
        if self.hint:
            message += f"\nHint: {self.hint}"
        if self.example:
            message += f"\nExample:\n{self.example}"
        return message
