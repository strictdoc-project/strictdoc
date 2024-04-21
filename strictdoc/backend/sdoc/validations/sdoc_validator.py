# mypy: disable-error-code="arg-type,no-redef,no-untyped-call,no-untyped-def,union-attr"
import re
from typing import Iterator, Optional, Set

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldTag,
    RequirementFieldName,
)


def multi_choice_regex_match(value):
    keyword = "[a-zA-Z0-9_]+"
    regex = re.compile(rf"^{keyword}(, {keyword})*$")
    match = regex.match(value)
    return match is not None


class SDocValidator:
    """
    This helper class is used for validating SDoc documents right after the
    textX parsing and processing steps have finished.
    FIXME: In the future, all processing validation steps could be moved to this
           class as well. This would remove the need in the ParseContext class
           and simplify several other implementation details.
    """

    @staticmethod
    def validate_document(document: SDocDocument):
        assert isinstance(document, SDocDocument), document
        SDocValidator._validate_document_config(document)
        SDocValidator._validate_document_view(document)

    @staticmethod
    def _validate_document_config(document: SDocDocument):
        document_config: DocumentConfig = document.config
        if document_config.default_view is not None:
            if document.view is None:
                raise StrictDocSemanticError.default_view_doesnt_exist(
                    document=document,
                    document_config=document_config,
                    default_view=document_config.default_view,
                )
            else:
                view_names = map(
                    lambda view_: view_.view_id, document.view.views
                )
                if document_config.default_view not in view_names:
                    raise StrictDocSemanticError.default_view_doesnt_exist(
                        document=document,
                        document_config=document_config,
                        default_view=document_config.default_view,
                    )

    @staticmethod
    def _validate_document_view(document: SDocDocument):
        document_view: Optional[DocumentView] = document.view
        if document_view is not None:
            for view in document_view.views:
                for tag in view.tags:
                    if (
                        tag.object_type
                        not in document.grammar.registered_elements
                    ):
                        raise StrictDocSemanticError.view_references_nonexisting_grammar_element(
                            document,
                            document_view,
                            view,
                            tag.object_type,
                        )
                    for field in tag.visible_fields:
                        for grammar_element in document.grammar.elements:
                            if field.name not in grammar_element.fields_map:
                                raise StrictDocSemanticError.view_references_nonexisting_field(
                                    document,
                                    document_view,
                                    view,
                                    tag.object_type,
                                    field.name,
                                )

    @staticmethod
    def validate_node(
        requirement: SDocNode,
        document_grammar: DocumentGrammar,
        path_to_sdoc_file: str,
    ):
        if (
            requirement.requirement_type
            not in document_grammar.registered_elements
        ):
            raise StrictDocSemanticError.unknown_requirement_type(
                requirement, path_to_sdoc_file
            )

        grammar_element = document_grammar.elements_by_type[
            requirement.requirement_type
        ]
        registered_fields: Set[str] = set(grammar_element.get_field_titles())

        for field_name in requirement.ordered_fields_lookup:
            if field_name not in registered_fields and field_name != "REFS":
                raise StrictDocSemanticError.unregistered_field(
                    field_name=field_name,
                    requirement=requirement,
                    document_grammar=document_grammar,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

        grammar_element: GrammarElement = document_grammar.elements_by_type[
            requirement.requirement_type
        ]
        grammar_fields_iterator: Iterator[GrammarElementField] = iter(
            grammar_element.fields
        )
        requirement_field_iterator: Iterator[SDocNodeField] = iter(
            requirement.fields_as_parsed
        )

        requirement_field: Optional[SDocNodeField] = next(
            requirement_field_iterator, None
        )
        grammar_field: Optional[GrammarElementField] = next(
            grammar_fields_iterator, None
        )

        refs_requirement_field = None
        while True:
            if (
                requirement_field is not None
                and requirement_field.field_name == "REFS"
            ):
                refs_requirement_field = requirement_field
                requirement_field = next(requirement_field_iterator, None)
            if grammar_field is not None and grammar_field.title == "REFS":
                grammar_field = next(grammar_fields_iterator, None)
            try:
                valid_or_not_required_field = (
                    SDocValidator.validate_requirement_field(
                        requirement,
                        document_grammar,
                        requirement_field=requirement_field,
                        grammar_field=grammar_field,
                        path_to_sdoc_file=path_to_sdoc_file,
                    )
                )
            except StopIteration:
                break
            if valid_or_not_required_field:
                # COMMENT can appear multiple times.
                if requirement_field.field_name == RequirementFieldName.COMMENT:
                    requirement_field = next(requirement_field_iterator, None)
                    break
                grammar_field = next(grammar_fields_iterator, None)
                requirement_field = next(requirement_field_iterator, None)
            else:
                assert not grammar_field.required
                grammar_field = next(grammar_fields_iterator, None)

        # REFS validation.

        if refs_requirement_field is not None:
            requirement_field_value_references = (
                refs_requirement_field.field_value_references
            )

            for reference in requirement_field_value_references:
                if not grammar_element.has_relation_type_role(
                    relation_type=reference.ref_type,
                    relation_role=reference.role,
                ):
                    raise StrictDocSemanticError.invalid_reference_type_item(
                        node=requirement,
                        reference_item=reference,
                        path_to_sdoc_file=path_to_sdoc_file,
                    )

    @staticmethod
    def validate_requirement_field(
        requirement: SDocNode,
        document_grammar: DocumentGrammar,
        requirement_field: SDocNodeField,
        grammar_field: GrammarElementField,
        path_to_sdoc_file: str,
    ) -> bool:
        if grammar_field is None:
            if requirement_field is None:
                # Both grammar and requirements fields are over.
                # Validation is done.
                raise StopIteration

            # Unexpected field outside grammar.
            raise StrictDocSemanticError.wrong_field_order(
                node=requirement,
                document_grammar=document_grammar,
                problematic_field=requirement_field,
                path_to_sdoc_file=path_to_sdoc_file,
            )

        # No more requirement fields. Checking if all remaining grammar fields
        # are non-required.
        if requirement_field is None:
            if grammar_field.required:
                raise StrictDocSemanticError.missing_required_field(
                    node=requirement,
                    grammar_field=grammar_field,
                    document_grammar=document_grammar,
                    path_to_sdoc_file=path_to_sdoc_file,
                )
            return False

        if grammar_field.title != requirement_field.field_name:
            if grammar_field.required:
                raise StrictDocSemanticError.wrong_field_order(
                    node=requirement,
                    document_grammar=document_grammar,
                    problematic_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )
            return False
        if isinstance(grammar_field, GrammarElementFieldSingleChoice):
            if requirement_field.field_value not in grammar_field.options:
                raise StrictDocSemanticError.invalid_choice_field(
                    node=requirement,
                    document_grammar=document_grammar,
                    requirement_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

        elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
            requirement_field_value = requirement_field.field_value

            if not multi_choice_regex_match(requirement_field_value):
                raise StrictDocSemanticError.not_comma_separated_choices(
                    node=requirement,
                    requirement_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

            requirement_field_value_components = requirement_field_value.split(
                ", "
            )
            for component in requirement_field_value_components:
                if component not in grammar_field.options:
                    raise StrictDocSemanticError.invalid_multiple_choice_field(
                        node=requirement,
                        document_grammar=document_grammar,
                        requirement_field=requirement_field,
                        path_to_sdoc_file=path_to_sdoc_file,
                    )

        elif isinstance(grammar_field, GrammarElementFieldTag):
            requirement_field_value = requirement_field.field_value

            if not multi_choice_regex_match(requirement_field_value):
                raise StrictDocSemanticError.not_comma_separated_tag_field(
                    node=requirement,
                    requirement_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

        return True
