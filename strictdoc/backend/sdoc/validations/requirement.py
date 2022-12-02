import re
from typing import Optional, Set, Iterator

from textx import get_location

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElementField,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldTag,
    GrammarElementFieldReference,
    RequirementFieldName,
    ReferenceType,
)


def multi_choice_regex_match(value):
    keyword = "[a-zA-Z0-9_]+"
    regex = re.compile(rf"^{keyword}(, {keyword})*$")
    match = regex.match(value)
    return match is not None


def validate_requirement(
    requirement: Requirement, document_grammar: DocumentGrammar
):
    registered_fields: Set[str] = document_grammar.fields_order_by_type[
        requirement.requirement_type
    ]
    for field_name in requirement.ordered_fields_lookup:
        if field_name not in registered_fields:
            raise StrictDocSemanticError.unregistered_field(
                field_name=field_name,
                requirement=requirement,
                document_grammar=document_grammar,
                **get_location(requirement),
            )

    grammar_element: GrammarElement = document_grammar.elements_by_type[
        requirement.requirement_type
    ]
    grammar_fields_iterator: Iterator[GrammarElementField] = iter(
        grammar_element.fields
    )
    requirement_field_iterator: Iterator[RequirementField] = iter(
        requirement.fields
    )

    requirement_field: Optional[RequirementField] = next(
        requirement_field_iterator, None
    )
    grammar_field: Optional[GrammarElementField] = next(
        grammar_fields_iterator, None
    )

    while True:
        try:
            valid_or_not_required_field = validate_requirement_field(
                requirement,
                document_grammar,
                requirement_field=requirement_field,
                grammar_field=grammar_field,
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


def validate_requirement_field(
    requirement: Requirement,
    document_grammar: DocumentGrammar,
    requirement_field: RequirementField,
    grammar_field: GrammarElementField,
) -> bool:
    if grammar_field is None:
        if requirement_field is None:
            # Both grammar and requirements fields are over.
            # Validation is done.
            raise StopIteration

        # Unexpected field outside grammar.
        raise StrictDocSemanticError.wrong_field_order(
            requirement=requirement,
            document_grammar=document_grammar,
            problematic_field=requirement_field,
            **get_location(requirement),
        )

    # No more requirement fields. Checking if all remaining grammar fields
    # are non-required.
    if requirement_field is None:
        if grammar_field.required:
            raise StrictDocSemanticError.missing_required_field(
                requirement=requirement,
                grammar_field=grammar_field,
                document_grammar=document_grammar,
                **get_location(requirement),
            )
        return False

    if grammar_field.title != requirement_field.field_name:
        if grammar_field.required:
            raise StrictDocSemanticError.wrong_field_order(
                requirement=requirement,
                document_grammar=document_grammar,
                problematic_field=requirement_field,
                **get_location(requirement),
            )
        return False
    if isinstance(grammar_field, GrammarElementFieldSingleChoice):
        if requirement_field.field_value not in grammar_field.options:
            raise StrictDocSemanticError.invalid_choice_field(
                requirement=requirement,
                document_grammar=document_grammar,
                requirement_field=requirement_field,
                **get_location(requirement),
            )

    elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
        requirement_field_value = requirement_field.field_value

        if not multi_choice_regex_match(requirement_field_value):
            raise StrictDocSemanticError.not_comma_separated_choices(
                requirement_field=requirement_field,
                **get_location(requirement),
            )

        requirement_field_value_components = requirement_field_value.split(", ")
        for component in requirement_field_value_components:
            if component not in grammar_field.options:
                raise StrictDocSemanticError.invalid_multiple_choice_field(
                    requirement=requirement,
                    document_grammar=document_grammar,
                    requirement_field=requirement_field,
                    **get_location(requirement),
                )

    elif isinstance(grammar_field, GrammarElementFieldTag):
        requirement_field_value = requirement_field.field_value

        if not multi_choice_regex_match(requirement_field_value):
            raise StrictDocSemanticError.not_comma_separated_tag_field(
                requirement_field=requirement_field,
                **get_location(requirement),
            )

    elif isinstance(grammar_field, GrammarElementFieldReference):
        requirement_field_value_references = (
            requirement_field.field_value_references
        )
        for reference in requirement_field_value_references:
            if (
                reference.ref_type in ReferenceType.GRAMMAR_REFERENCE_TYPE_MAP
                and ReferenceType.GRAMMAR_REFERENCE_TYPE_MAP[reference.ref_type]
                in grammar_field.types
            ):
                continue
            raise StrictDocSemanticError.invalid_reference_type_item(
                requirement=requirement,
                document_grammar=document_grammar,
                requirement_field=requirement_field,
                reference_item=reference,
                **get_location(requirement),
            )

    return True
