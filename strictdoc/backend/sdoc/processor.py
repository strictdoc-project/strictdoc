from typing import Optional

from textx import get_location

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.backend.sdoc.models.fragment_from_file import FragmentFromFile
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
    def __init__(self, parse_context: ParseContext, delegate):
        self.parse_context: ParseContext = parse_context
        self.delegate = delegate

    def process_document(self, document: Document):
        document.grammar = self.parse_context.document_grammar

    def get_default_processors(self):
        return {
            "Document": self.process_document,
            "DocumentConfig": self.process_document_config,
            "DocumentGrammar": self.process_document_grammar,
            "Section": self.process_section,
            "FragmentFromFile": self.process_include,
            "CompositeRequirement": self.process_composite_requirement,
            "Requirement": self.process_requirement,
            "FreeText": self.process_free_text,
            "Fragment": self.process_fragment,
        }

    def process_document_config(self, document_config: DocumentConfig):
        self.parse_context.document_config = document_config

    def process_document_grammar(self, document_grammar: DocumentGrammar):
        self.parse_context.document_grammar = document_grammar

    def process_section(self, section: Section):
        section.ng_document_reference = self.parse_context.document_reference

        if self.parse_context.document_config.auto_levels:
            if section.level and section.level != "None":
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

        self._resolve_parents(section)
        assert section.ng_level > 0

    def process_include(self, include: FragmentFromFile):
        self._resolve_parents(include)
        self.parse_context.current_include_parent = include.parent

        assert self.delegate is not None
        fragment = self.delegate(include, self.parse_context)

        parent_section_contents = include.parent.section_contents
        index = parent_section_contents.index(include)
        before = parent_section_contents[:index]
        index = (
            index + 1
        )  # black and flake8 fight to put a space before ':' otherwise
        after = parent_section_contents[index:]

        include.parent.section_contents = []
        include.parent.section_contents.extend(before)
        include.parent.section_contents.extend(fragment.section_contents)
        include.parent.section_contents.extend(after)

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
            self._resolve_parents(composite_requirement)
        elif isinstance(composite_requirement.parent, CompositeRequirement):
            self._resolve_parents(composite_requirement)
            assert composite_requirement.parent.ng_level
        elif isinstance(composite_requirement.parent, Document):
            composite_requirement.ng_level = 1
        elif isinstance(composite_requirement.parent, Fragment):
            composite_requirement.ng_level = (
                self.parse_context.current_include_parent.ng_level + 1
            )
        else:
            raise NotImplementedError

        # TODO: there is now walking up the parents 2 times
        # (ng_levels and here).
        cursor = composite_requirement.parent
        while not self.is_top_level(cursor) and not cursor.ng_has_requirements:
            cursor.ng_has_requirements = True
            cursor = cursor.parent

        if (
            composite_requirement.title is None
            or not self.parse_context.document_config.is_requirement_in_toc()
        ) and self.parse_context.document_config.auto_levels:
            composite_requirement.level = "None"

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
            self._resolve_parents(requirement)
        elif isinstance(requirement.parent, CompositeRequirement):
            self._resolve_parents(requirement)
        elif isinstance(requirement.parent, Document):
            requirement.ng_level = 1
        elif isinstance(requirement.parent, Fragment):
            requirement.ng_level = (
                self.parse_context.current_include_parent.ng_level + 1
            )
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

        if (
            requirement.title is None
            or not self.parse_context.document_config.is_requirement_in_toc()
        ) and self.parse_context.document_config.auto_levels:
            requirement.level = "None"

    def process_free_text(self, free_text):
        if isinstance(free_text.parent, Section):
            self._resolve_parents(free_text)
        elif isinstance(free_text.parent, CompositeRequirement):
            self._resolve_parents(free_text)
        elif isinstance(free_text.parent, Document):
            free_text.ng_level = 1
        elif isinstance(free_text.parent, Fragment):
            free_text.ng_level = (
                self.parse_context.current_include_parent.ng_level + 1
            )
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

        section_with_none_level = cursor.level == "None"
        for parent_idx, parent in enumerate(reversed(parents_to_resolve_level)):
            parent.ng_level = cursor_level + parent_idx + 1
            if isinstance(parent, (Section, CompositeRequirement)):
                if section_with_none_level:
                    parent.level = "None"
                elif parent.level == "None":
                    section_with_none_level = True
        node.ng_level = node.parent.ng_level + 1
        if section_with_none_level:
            node.level = "None"
