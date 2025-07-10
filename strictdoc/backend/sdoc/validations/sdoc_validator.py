# mypy: disable-error-code="arg-type,union-attr"
import re
from typing import Iterator, Optional, Set

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldTag,
)
from strictdoc.backend.sdoc.models.model import RequirementFieldName
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.helpers.cast import assert_optional_cast

MULTIPLE_CHOICE_FIELD_KW = r"[a-zA-Z0-9\/\-_ ]+"
MULTIPLE_CHOICE_FIELD_REGEX = re.compile(
    rf"^{MULTIPLE_CHOICE_FIELD_KW}(, {MULTIPLE_CHOICE_FIELD_KW})*$"
)


def multi_choice_regex_match(value: str) -> bool:
    """
    Validate MultipleChoice field value.

    Bug: Forward slashes in field values cause errors #2197,
    https://github.com/strictdoc-project/strictdoc/issues/2197
    """

    match = MULTIPLE_CHOICE_FIELD_REGEX.match(value)
    return match is not None


class SDocValidator:
    """
    Class that validates SDoc after textX parsing and processing steps.

    FIXME: In the future, all processing validation steps could be moved to this
           class as well. This would remove the need in the ParseContext class
           and simplify several other implementation details.
    """

    @staticmethod
    def validate_document(document: SDocDocument) -> None:
        assert isinstance(document, SDocDocument), document
        SDocValidator._validate_document_config(document)
        SDocValidator._validate_document_view(document)
        SDocValidator._validate_grammar(document)

    @staticmethod
    def validate_grammar_from_file(
        path_to_grammar: str, grammar_from_file: DocumentGrammar
    ) -> None:
        for grammar_element_ in grammar_from_file.elements:
            SDocValidator.validate_grammar_element(
                path_to_grammar, grammar_element_
            )

    @staticmethod
    def _validate_grammar(document: SDocDocument) -> None:
        assert document.meta is not None
        assert document.grammar is not None
        for grammar_element_ in document.grammar.elements:
            SDocValidator.validate_grammar_element(
                document.meta.input_doc_full_path, grammar_element_
            )

    @staticmethod
    def validate_grammar_element(
        path_to_grammar: str, grammar_element: GrammarElement
    ) -> None:
        # GrammarFromFile doesn't have a parent document.
        document: Optional[SDocDocument] = assert_optional_cast(
            grammar_element.parent.parent, SDocDocument
        )
        if document is not None and document.config.enable_mid:
            if (
                grammar_element.tag != "TEXT"
                and "MID" not in grammar_element.fields_map
            ):
                raise StrictDocSemanticError.grammar_element_has_no_mid_field(
                    grammar_element,
                    path_to_grammar,
                )

    @staticmethod
    def _validate_document_config(document: SDocDocument) -> None:
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
    def _validate_document_view(document: SDocDocument) -> None:
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

                    grammar_element: GrammarElement = (
                        document.grammar.elements_by_type[tag.object_type]
                    )
                    for field in tag.visible_fields:
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
        auto_uid_mode: bool = False,
    ) -> None:
        if requirement.node_type not in document_grammar.registered_elements:
            raise StrictDocSemanticError.unknown_node_type(
                requirement, path_to_sdoc_file
            )

        grammar_element: GrammarElement = document_grammar.elements_by_type[
            requirement.node_type
        ]

        if requirement.is_composite:
            if not grammar_element.property_is_composite:
                raise StrictDocSemanticError.composite_node_and_non_composite_element_mismatch(
                    requirement, path_to_sdoc_file
                )
        else:
            if grammar_element.property_is_composite:
                raise StrictDocSemanticError.non_composite_node_and_composite_element_composite(
                    requirement, path_to_sdoc_file
                )

        registered_fields: Set[str] = set(grammar_element.get_field_titles())

        for field_name in requirement.ordered_fields_lookup:
            if field_name not in registered_fields:
                raise StrictDocSemanticError.unregistered_field(
                    field_name=field_name,
                    requirement=requirement,
                    document_grammar=document_grammar,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

        grammar_fields_iterator: Iterator[GrammarElementField] = iter(
            grammar_element.fields
        )
        requirement_field_iterator: Iterator[SDocNodeField] = (
            requirement.enumerate_fields()
        )

        requirement_field: Optional[SDocNodeField] = next(
            requirement_field_iterator, None
        )
        grammar_field: Optional[GrammarElementField] = next(
            grammar_fields_iterator, None
        )

        while True:
            try:
                valid_or_not_required_field = (
                    SDocValidator.validate_requirement_field(
                        requirement,
                        document_grammar,
                        requirement_field=requirement_field,
                        grammar_field=grammar_field,
                        path_to_sdoc_file=path_to_sdoc_file,
                        auto_uid_mode=auto_uid_mode,
                    )
                )
            except StopIteration:
                break
            if valid_or_not_required_field:
                # COMMENT can appear multiple times.
                if requirement_field.field_name == RequirementFieldName.COMMENT:
                    requirement_field = next(requirement_field_iterator, None)
                    if (
                        requirement_field is not None
                        and requirement_field.field_name
                        == RequirementFieldName.COMMENT
                    ):
                        continue
                    else:
                        grammar_field = next(grammar_fields_iterator, None)
                        continue
                grammar_field = next(grammar_fields_iterator, None)
                requirement_field = next(requirement_field_iterator, None)
            else:
                assert not grammar_field.required or (
                    grammar_field.title == "UID" and auto_uid_mode
                )
                grammar_field = next(grammar_fields_iterator, None)

        # REFS validation.
        for reference in requirement.relations:
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
        auto_uid_mode: bool = True,
    ) -> bool:
        """
        Validate a single node field using its grammar element field definition.
        """
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
                if (
                    grammar_field.title
                    not in requirement.ordered_fields_lookup.keys()
                ):
                    if grammar_field.title == "UID" and auto_uid_mode:
                        return False

                    raise StrictDocSemanticError.missing_required_field(
                        node=requirement,
                        grammar_field=grammar_field,
                        document_grammar=document_grammar,
                        path_to_sdoc_file=path_to_sdoc_file,
                    )

                raise StrictDocSemanticError.wrong_field_order(
                    node=requirement,
                    document_grammar=document_grammar,
                    problematic_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )
            return False

        requirement_field_text_value = requirement_field.get_text_value()

        if isinstance(grammar_field, GrammarElementFieldSingleChoice):
            if requirement_field_text_value not in grammar_field.options:
                raise StrictDocSemanticError.invalid_choice_field(
                    node=requirement,
                    document_grammar=document_grammar,
                    requirement_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

        elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
            if not multi_choice_regex_match(requirement_field_text_value):
                raise StrictDocSemanticError.not_comma_separated_choices(
                    node=requirement,
                    requirement_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

            requirement_field_value_components = (
                requirement_field_text_value.split(", ")
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
            if not multi_choice_regex_match(requirement_field_text_value):
                raise StrictDocSemanticError.not_comma_separated_tag_field(
                    node=requirement,
                    requirement_field=requirement_field,
                    path_to_sdoc_file=path_to_sdoc_file,
                )

        return True
