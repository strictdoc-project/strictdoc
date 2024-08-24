# mypy: disable-error-code="attr-defined,no-untyped-call,no-untyped-def,union-attr"
from textx import TextXSyntaxError

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
    GrammarElementField,
)
from strictdoc.backend.sdoc.models.document_view import (
    DocumentView,
    ViewElement,
)
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
    def unknown_node_type(node: SDocNode, path_to_sdoc_file: str):
        return StrictDocSemanticError(
            title=f"Invalid node type: {node.node_type}.",
            hint=None,
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def unregistered_field(
        *,
        field_name: str,
        requirement: SDocNode,
        document_grammar: DocumentGrammar,
        path_to_sdoc_file: str,
    ):
        grammar_dump = document_grammar.dump_fields(requirement.node_type)
        return StrictDocSemanticError(
            title=f"Invalid requirement field: {field_name}",
            hint=(
                f"Compare with the document grammar: [{grammar_dump}] "
                f"for type: {requirement.node_type}."
            ),
            example=None,
            line=requirement.ng_line_start,
            col=requirement.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def missing_required_field(
        node: SDocNode,
        grammar_field: GrammarElementField,
        document_grammar: DocumentGrammar,
        path_to_sdoc_file: str,
    ):
        grammar_fields = document_grammar.dump_fields(node.node_type)
        return StrictDocSemanticError(
            title=(
                f"Requirement is missing a field that is required by "
                f"grammar: {grammar_field.title}."
            ),
            hint=(
                f"Requirement fields: [{node.dump_fields_as_parsed()}], "
                f"grammar fields: [{grammar_fields}]."
            ),
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def unexpected_field_outside_grammar(
        node: SDocNode,
        requirement_field: SDocNodeField,
        document_grammar: DocumentGrammar,
        path_to_sdoc_file: str,
    ):
        grammar_fields = document_grammar.dump_fields(node.node_type)
        return StrictDocSemanticError(
            title=(
                f"Unexpected field outside grammar: "
                f"{requirement_field.field_name}"
            ),
            hint=(
                f"Requirement fields: [{node.dump_fields_as_parsed()}], "
                f"grammar fields: [{grammar_fields}]."
            ),
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def wrong_field_order(
        node: SDocNode,
        document_grammar: DocumentGrammar,
        problematic_field: SDocNodeField,
        path_to_sdoc_file: str,
    ):
        assert isinstance(
            problematic_field, SDocNodeField
        ), f"{problematic_field}"
        requirement_dump = node.dump_fields_as_parsed()
        grammar_dump = document_grammar.dump_fields(node.node_type)
        return StrictDocSemanticError(
            title=f"Wrong field order for requirement: [{requirement_dump}].",
            hint=(
                f"Problematic field: {problematic_field.field_name}. "
                f"Compare with the document grammar: [{grammar_dump}] "
                f"for type: {node.node_type}."
            ),
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def invalid_choice_field(
        node: SDocNode,
        document_grammar: DocumentGrammar,
        requirement_field: SDocNodeField,
        path_to_sdoc_file: str,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field has an invalid SingleChoice value: "
                f"{requirement_field.get_text_value()}."
            ),
            hint=(
                f"Problematic field: {requirement_field.field_name}. "
                f"Compare with the document grammar: "
                f"["
                f"{document_grammar.dump_fields(node.node_type)}"
                f"] "
                f"for type: {node.node_type}."
            ),
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def invalid_multiple_choice_field(
        node: SDocNode,
        document_grammar: DocumentGrammar,
        requirement_field: SDocNodeField,
        path_to_sdoc_file: str,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field has an invalid MultipleChoice value: "
                f"{requirement_field.get_text_value()}."
            ),
            hint=(
                f"Problematic field: {requirement_field.field_name}. "
                f"Compare with the document grammar: "
                f"["
                f"{document_grammar.dump_fields(node.node_type)}"
                f"] "
                f"for type: {node.node_type}."
            ),
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def not_comma_separated_choices(
        node: SDocNode,
        requirement_field: SDocNodeField,
        path_to_sdoc_file,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field of type MultipleChoice is invalid: "
                f"{requirement_field.get_text_value()}."
            ),
            hint="MultipleChoice field requires ', '-separated values.",
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def not_comma_separated_tag_field(
        node: SDocNode,
        requirement_field: SDocNodeField,
        path_to_sdoc_file: str,
    ):
        return StrictDocSemanticError(
            title=(
                f"Requirement field of type Tag is invalid: "
                f"{requirement_field.get_text_value()}."
            ),
            hint="Tag field requires ', '-separated values.",
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def invalid_reference_type_item(
        node: SDocNode,
        reference_item: Reference,
        path_to_sdoc_file: str,
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
            hint=f"Problematic requirement: {node.reserved_uid}.",
            example=None,
            line=node.ng_line_start,
            col=node.ng_col_start,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def grammar_missing_reserved_statement(
        grammar_element: GrammarElement,
        path_to_sdoc_file: str,
        line: int,
        column: int,
    ):
        return StrictDocSemanticError(
            title=(
                f"Grammar element '{grammar_element.tag}' is missing a reserved"
                " content field declaration, one of {STATEMENT, DESCRIPTION, CONTENT}."
            ),
            hint=(
                "A content field plays a key role in StrictDoc's HTML user interface "
                "as well as in the other export formats. It is a reserved field"
                " that any grammar element must have."
            ),
            example=None,
            line=line,
            col=column,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def grammar_reserved_statement_must_be_required(
        grammar_element: GrammarElement,
        field_title: str,
        path_to_sdoc_file: str,
        line: int,
        column: int,
    ):
        return StrictDocSemanticError(
            title=(
                f"Grammar element '{grammar_element.tag}'s {field_title} field "
                f"must be declared as 'REQUIRED: True'."
            ),
            hint=(
                "A content field plays a key role in StrictDoc's HTML user interface "
                "as well as in the other export formats. It is a reserved field"
                " that any grammar element must have with 'REQUIRED: True'."
            ),
            example=None,
            line=line,
            col=column,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def grammar_element_has_no_mid_field(
        grammar_element: GrammarElement,
        path_to_sdoc_file: str,
    ):
        return StrictDocSemanticError(
            title=(
                f"Grammar element '{grammar_element.tag}' is missing the MID field "
                f"which contradicts to the DOCUMENT's ENABLE_MID setting."
            ),
            hint=(
                "Either disable the ENABLE_MID option or ensure that every element has the MID field defined."
            ),
            example=None,
            line=1,
            col=1,
            filename=path_to_sdoc_file,
        )

    @staticmethod
    def view_references_nonexisting_grammar_element(
        document: SDocDocument,
        document_view: DocumentView,
        view_element: ViewElement,
        object_type: str,
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
            line=document_view.ng_line_start,
            col=document_view.ng_col_start,
            filename=document.meta.input_doc_full_path,
        )

    @staticmethod
    def view_references_nonexisting_field(
        document: SDocDocument,
        document_view: DocumentView,
        view_element: ViewElement,
        object_type: str,
        field_name: str,
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
            line=document_view.ng_line_start,
            col=document_view.ng_col_start,
            filename=document.meta.input_doc_full_path,
        )

    @staticmethod
    def default_view_doesnt_exist(
        document: SDocDocument,
        document_config: DocumentConfig,
        default_view: str,
    ):
        filename = document.meta.input_doc_full_path

        return StrictDocSemanticError(
            title=(
                f"Default view '{default_view}' does not exist in the document."
            ),
            hint=(
                "Make sure that the specified default view is created in the "
                "VIEWS configuration."
            ),
            example=None,
            line=document_config.ng_line_start,
            col=document_config.ng_col_start,
            filename=filename,
        )

    def to_print_message(self) -> str:
        message = ""
        message += f"error: could not parse file: {self.file_path}.\n"
        message += f"Semantic error: {self.title}\n"
        message += f"Location: {self.file_path}:{self.line}:{self.col}"
        if self.hint:
            message += f"\nHint: {self.hint}"
        if self.example:
            message += f"\nExample:\n{self.example}"
        return message
