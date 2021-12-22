from typing import Optional

from textx import get_location

from strictdoc.backend.dsl.document_reference import DocumentReference
from strictdoc.backend.dsl.error_handling import StrictDocSemanticError
from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.requirement import CompositeRequirement
from strictdoc.backend.dsl.models.section import Section


class ParseContext:
    def __init__(self):
        self.document_reference: DocumentReference = DocumentReference()
        self.document_config: Optional[DocumentConfig] = None


class SDocParsingProcessor:
    def __init__(self, parse_context: ParseContext):
        self.parse_context: ParseContext = parse_context

    @staticmethod
    def process_document(document: Document):
        if document.legacy_title_is_used:
            print(
                "warning: [DOCUMENT].NAME field is deprecated."
                " Now both [DOCUMENT]s and [SECTION]s have 'TITLE:'."
                " Use 'TITLE:' instead."
            )

    def process_document_config(self, document_config: DocumentConfig):
        self.parse_context.document_config = document_config

    def process_section(self, section: Section):
        section.ng_document_reference = self.parse_context.document_reference

        if self.parse_context.document_config.auto_levels:
            if section.level:
                print(
                    "warning: [SECTION].LEVEL field is provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to On. "
                    f"Section: {section}"
                )
        else:
            if not section.level:
                print(
                    "warning: [SECTION].LEVEL field is not provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to Off. "
                    f"Section: {section}"
                )

        if section.parent.ng_level is None:
            SDocParsingProcessor._resolve_parents(section)
        section.ng_level = section.parent.ng_level + 1
        assert section.ng_level > 0
        section.parent.ng_sections.append(section)

    def process_composite_requirement(
        self, composite_requirement: CompositeRequirement
    ):
        if self.parse_context.document_config.auto_levels:
            if composite_requirement.level:
                print(
                    "warning: [COMPOSITE_REQUIREMENT].LEVEL field is provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to On. "
                    f"Composite requirement: {composite_requirement}"
                )
        else:
            if not composite_requirement.level:
                print(
                    "warning: [COMPOSITE_REQUIREMENT].LEVEL field is not "
                    "provided. This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to Off. "
                    f"Composite requirement: {composite_requirement}"
                )

        composite_requirement.ng_document_reference = (
            self.parse_context.document_reference
        )

        if isinstance(composite_requirement.parent, Section):
            if composite_requirement.parent.ng_level is None:
                SDocParsingProcessor._resolve_parents(composite_requirement)
            composite_requirement.ng_level = (
                composite_requirement.parent.ng_level + 1
            )
            composite_requirement.parent.ng_sections.append(
                composite_requirement
            )
        elif isinstance(composite_requirement.parent, CompositeRequirement):
            if composite_requirement.parent.ng_level is None:
                SDocParsingProcessor._resolve_parents(composite_requirement)
            assert composite_requirement.parent.ng_level
            composite_requirement.ng_level = (
                composite_requirement.parent.ng_level + 1
            )
        elif isinstance(composite_requirement.parent, Document):
            composite_requirement.ng_level = 1
        else:
            raise NotImplementedError

        # TODO: there is now walking up the parents 2 times
        # (ng_levels and here).
        cursor = composite_requirement.parent
        while (
            not isinstance(cursor, Document) and not cursor.ng_has_requirements
        ):
            cursor.ng_has_requirements = True
            cursor = cursor.parent

    def process_requirement(self, requirement):
        # Validation
        if self.parse_context.document_config.auto_levels:
            if requirement.level:
                print(
                    "warning: [REQUIREMENT].LEVEL field is provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to On. "
                    f"Requirement: {requirement}"
                )
        else:
            if not requirement.level:
                print(
                    "warning: [REQUIREMENT].LEVEL field is not provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to Off. "
                    f"Requirement: {requirement}"
                )

        special_fields = requirement.special_fields
        if special_fields:
            document_config = self.parse_context.document_config
            if not document_config:
                raise StrictDocSemanticError.missing_special_fields(
                    special_fields,
                    **get_location(requirement),
                )
            config_special_fields = document_config.special_fields
            if not config_special_fields:
                raise StrictDocSemanticError.missing_special_fields(
                    special_fields,
                    **get_location(requirement),
                )

            special_field_set = set()
            for special_field in special_fields:
                if (
                    special_field.field_name
                    not in document_config.special_fields_set
                ):
                    raise StrictDocSemanticError.field_is_missing_in_doc_config(
                        special_field.field_name,
                        special_field.field_value,
                        **get_location(requirement),
                    )
                special_field_set.add(special_field.field_name)

            for (
                required_special_field
            ) in document_config.special_fields_required:
                if required_special_field not in special_field_set:
                    # fmt: off
                    raise (
                        StrictDocSemanticError.
                        requirement_missing_required_field(
                            required_special_field, **get_location(requirement)
                        )
                    )
                    # fmt: on
        else:
            document_config = self.parse_context.document_config
            if document_config:
                if len(document_config.special_fields_required) > 0:
                    # fmt: off
                    raise (
                        StrictDocSemanticError.
                        requirement_missing_special_fields(
                            document_config.special_fields_required,
                            **get_location(requirement),
                        )
                    )
                    # fmt: on

        requirement.ng_document_reference = (
            self.parse_context.document_reference
        )

        if isinstance(requirement.parent, Section):
            if requirement.parent.ng_level is None:
                SDocParsingProcessor._resolve_parents(requirement)
            requirement.ng_level = requirement.parent.ng_level + 1
        elif isinstance(requirement.parent, CompositeRequirement):
            if requirement.parent.ng_level is None:
                SDocParsingProcessor._resolve_parents(requirement)
            requirement.ng_level = requirement.parent.ng_level + 1
        elif isinstance(requirement.parent, Document):
            requirement.ng_level = 1
        else:
            raise NotImplementedError

        # TODO: there is now walking up the parents 2 times (ng_levels
        # and here).
        cursor = requirement.parent
        while (
            not isinstance(cursor, Document) and not cursor.ng_has_requirements
        ):
            cursor.ng_has_requirements = True
            cursor = cursor.parent

    @staticmethod
    def process_free_text(free_text):
        if isinstance(free_text.parent, Section):
            if free_text.parent.ng_level is None:
                SDocParsingProcessor._resolve_parents(free_text)
            free_text.ng_level = free_text.parent.ng_level + 1
        elif isinstance(free_text.parent, CompositeRequirement):
            if free_text.parent.ng_level is None:
                SDocParsingProcessor._resolve_parents(free_text)
            free_text.ng_level = free_text.parent.ng_level + 1
        elif isinstance(free_text.parent, Document):
            free_text.ng_level = 1
        else:
            raise NotImplementedError

    # During parsing, it is often the case that the node's parents do not have
    # their levels resolved yet. We go up the parent chain and resolve all of
    # the parents manually.
    @staticmethod
    def _resolve_parents(node):
        parents_to_resolve_level = []
        cursor = node.parent
        while cursor.ng_level is None:
            parents_to_resolve_level.append(cursor)
            cursor = cursor.parent
        for parent_idx, parent in enumerate(reversed(parents_to_resolve_level)):
            parent.ng_level = cursor.ng_level + parent_idx + 1
