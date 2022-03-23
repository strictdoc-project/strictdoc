from typing import Optional

from textx import get_location

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.backend.sdoc.models.include_from_file import IncludeFromFile
from strictdoc.backend.sdoc.models.requirement import (
    CompositeRequirement,
    Requirement,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.validations.requirement import validate_requirement


class ParseContext:
    def __init__(self):
        self.document_reference: DocumentReference = DocumentReference()
        self.document_config: Optional[DocumentConfig] = None
        self.document_grammar: DocumentGrammar = DocumentGrammar.create_default(
            None
        )
        self.current_include_parent = None


class SDocParsingProcessor:
    def __init__(self, parse_context: ParseContext):
        self.parse_context: ParseContext = parse_context

    def process_document(self, document: Document):
        if document.legacy_title_is_used:
            print(
                "warning: [DOCUMENT].NAME field is deprecated."
                " Now both [DOCUMENT]s and [SECTION]s have 'TITLE:'."
                " Use 'TITLE:' instead."
            )
        document.grammar = self.parse_context.document_grammar

    def process_document_config(self, document_config: DocumentConfig):
        self.parse_context.document_config = document_config

    def process_document_grammar(self, document_grammar: DocumentGrammar):
        self.parse_context.document_grammar = document_grammar

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
            self._resolve_parents(section)
        section.ng_level = section.parent.ng_level + 1
        assert section.ng_level > 0

    def process_include(self, include: IncludeFromFile):
        # pylint: disable=import-outside-toplevel
        from strictdoc.backend.sdoc.reader import (
            SDIReader,
        )  # can't import globally or else module loop ensues

        if include.parent.ng_level is None:
            self._resolve_parents(include)
        self.parse_context.current_include_parent = include.parent

        reader = SDIReader()
        fragment = reader.read_from_file(
            file_path=include.file, context=self.parse_context
        )
        assert isinstance(fragment, Fragment)

        include.parent.section_contents.extend(fragment.section_contents)
        include.parent.section_contents.remove(include)

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
                self._resolve_parents(composite_requirement)
            composite_requirement.ng_level = (
                composite_requirement.parent.ng_level + 1
            )
        elif isinstance(composite_requirement.parent, CompositeRequirement):
            if composite_requirement.parent.ng_level is None:
                self._resolve_parents(composite_requirement)
            assert composite_requirement.parent.ng_level
            composite_requirement.ng_level = (
                composite_requirement.parent.ng_level + 1
            )
        elif isinstance(composite_requirement.parent, Document):
            composite_requirement.ng_level = 1
        elif isinstance(composite_requirement.parent, Fragment):
            composite_requirement.ng_level = (
                self.parse_context.current_include_level + 1
            )
        else:
            raise NotImplementedError

        # TODO: there is now walking up the parents 2 times
        # (ng_levels and here).
        cursor = composite_requirement.parent
        while not self.is_top_level(cursor) and not cursor.ng_has_requirements:
            cursor.ng_has_requirements = True
            cursor = cursor.parent

    def process_requirement(self, requirement: Requirement):
        document_grammar = self.parse_context.document_grammar
        if (
            requirement.requirement_type
            not in document_grammar.registered_elements
        ):
            raise StrictDocSemanticError.unknown_requirement_type(
                requirement_type=requirement.requirement_type,
                **get_location(requirement),
            )

        validate_requirement(requirement, document_grammar)

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

        requirement.ng_document_reference = (
            self.parse_context.document_reference
        )

        if isinstance(requirement.parent, Section):
            if requirement.parent.ng_level is None:
                self._resolve_parents(requirement)
            requirement.ng_level = requirement.parent.ng_level + 1
        elif isinstance(requirement.parent, CompositeRequirement):
            if requirement.parent.ng_level is None:
                self._resolve_parents(requirement)
            requirement.ng_level = requirement.parent.ng_level + 1
        elif isinstance(requirement.parent, Document):
            requirement.ng_level = 1
        elif isinstance(requirement.parent, Fragment):
            requirement.ng_level = self.parse_context.current_include_level + 1
        else:
            raise NotImplementedError

        # TODO: there is now walking up the parents 2 times (ng_levels
        # and here).
        cursor = requirement.parent
        while not self.is_top_level(cursor) and not cursor.ng_has_requirements:
            cursor.ng_has_requirements = True
            if isinstance(cursor, Fragment):
                break
            cursor = cursor.parent

    def process_free_text(self, free_text):
        if isinstance(free_text.parent, Section):
            if free_text.parent.ng_level is None:
                self._resolve_parents(free_text)
            free_text.ng_level = free_text.parent.ng_level + 1
        elif isinstance(free_text.parent, CompositeRequirement):
            if free_text.parent.ng_level is None:
                self._resolve_parents(free_text)
            free_text.ng_level = free_text.parent.ng_level + 1
        elif isinstance(free_text.parent, Document):
            free_text.ng_level = 1
        elif isinstance(free_text.parent, Fragment):
            free_text.ng_level = self.parse_context.current_include_level + 1
        else:
            raise NotImplementedError

    def process_fragment(self, fragment: Fragment):
        pass

    @staticmethod
    def is_top_level(node):
        return isinstance(node, Document)

    # During parsing, it is often the case that the node's parents do not have
    # their levels resolved yet. We go up the parent chain and resolve all of
    # the parents manually.
    def _resolve_parents(self, node):
        parents_to_resolve_level = []
        cursor = node
        while cursor.ng_level is None:
            if isinstance(cursor.parent, Fragment):
                cursor.parent = self.parse_context.current_include_parent
                continue
            parents_to_resolve_level.append(cursor)
            cursor = cursor.parent
        cursor_level = cursor.ng_level

        for parent_idx, parent in enumerate(reversed(parents_to_resolve_level)):
            parent.ng_level = cursor_level + parent_idx + 1
