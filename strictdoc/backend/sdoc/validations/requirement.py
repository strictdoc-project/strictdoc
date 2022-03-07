import re
from typing import Optional

from textx import get_location

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElementField,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldTag,
)


def multi_choice_regex_match(value):
    keyword = "[a-zA-Z0-9_]+"
    regex = re.compile(rf"^{keyword}(, {keyword})*$")
    match = regex.match(value)
    return match is not None


def validate_requirement(
    requirement: Requirement, document_grammar: DocumentGrammar
):
    registered_fields = document_grammar.fields_order_by_type[
        requirement.requirement_type
    ]
    for field_name in requirement.ordered_fields_lookup:
        if field_name not in registered_fields:
            raise StrictDocSemanticError.unregistered_field(
                field_name=field_name,
                **get_location(requirement),
            )

    grammar_element_fields = document_grammar.elements_by_type[
        requirement.requirement_type
    ]
    grammar_fields_iterator = iter(grammar_element_fields.fields)
    requirement_field_iterator = iter(requirement.fields)

    requirement_field: Optional[RequirementField] = next(
        requirement_field_iterator, None
    )
    grammar_field: Optional[GrammarElementField] = next(
        grammar_fields_iterator, None
    )

    while True:
        if grammar_field is None:
            if requirement_field is None:
                break
            raise StrictDocSemanticError.unexpected_field_outside_grammar(
                requirement=requirement,
                requirement_field=requirement_field,
                document_grammar=document_grammar,
                **get_location(requirement),
            )
        if requirement_field is None:
            while grammar_field is not None:
                if grammar_field.required:
                    raise StrictDocSemanticError.missing_required_field(
                        requirement=requirement,
                        grammar_field=grammar_field,
                        document_grammar=document_grammar,
                        **get_location(requirement),
                    )
                grammar_field = next(grammar_fields_iterator, None)
            break

        valid_or_not_required_field = validate_requirement_field(
            requirement,
            document_grammar,
            requirement_field=requirement_field,
            grammar_element_field=grammar_field,
        )

        # COMMENT is a special case because there may be multiple comments.
        if grammar_field.title == "COMMENT":
            try:
                requirement_field = next(requirement_field_iterator)
                if requirement_field.field_name == "COMMENT":
                    continue
                grammar_field = next(grammar_fields_iterator, None)
            except StopIteration:
                requirement_field = None
                grammar_field = next(grammar_fields_iterator, None)
                continue

        if valid_or_not_required_field:
            requirement_field = next(requirement_field_iterator, None)
            grammar_field = next(grammar_fields_iterator, None)
        else:
            assert not grammar_field.required
            grammar_field = next(grammar_fields_iterator, None)


def validate_requirement_field(
    requirement: Requirement,
    document_grammar: DocumentGrammar,
    requirement_field: RequirementField,
    grammar_element_field: GrammarElementField,
) -> bool:
    assert isinstance(
        requirement_field, RequirementField
    ), f"{requirement_field}"
    assert isinstance(
        grammar_element_field, GrammarElementField
    ), f"{grammar_element_field}"
    if grammar_element_field.title != requirement_field.field_name:
        if grammar_element_field.required:
            raise StrictDocSemanticError.wrong_field_order(
                requirement=requirement,
                document_grammar=document_grammar,
                problematic_field=requirement_field,
                **get_location(requirement),
            )
        return False
    if isinstance(grammar_element_field, GrammarElementFieldSingleChoice):
        if requirement_field.field_value not in grammar_element_field.options:
            raise StrictDocSemanticError.invalid_choice_field(
                requirement=requirement,
                document_grammar=document_grammar,
                requirement_field=requirement_field,
                **get_location(requirement),
            )

    elif isinstance(grammar_element_field, GrammarElementFieldMultipleChoice):
        requirement_field_value = requirement_field.field_value

        if not multi_choice_regex_match(requirement_field_value):
            raise StrictDocSemanticError.not_comma_separated_choices(
                requirement_field=requirement_field,
                **get_location(requirement),
            )

        requirement_field_value_components = requirement_field_value.split(", ")
        for component in requirement_field_value_components:
            if component not in grammar_element_field.options:
                raise StrictDocSemanticError.invalid_multiple_choice_field(
                    requirement=requirement,
                    document_grammar=document_grammar,
                    requirement_field=requirement_field,
                    **get_location(requirement),
                )

    elif isinstance(grammar_element_field, GrammarElementFieldTag):
        requirement_field_value = requirement_field.field_value

        if not multi_choice_regex_match(requirement_field_value):
            raise StrictDocSemanticError.not_comma_separated_tag_field(
                requirement_field=requirement_field,
                **get_location(requirement),
            )
    return True
