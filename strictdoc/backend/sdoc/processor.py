# mypy: disable-error-code="arg-type,attr-defined,no-untyped-call,no-untyped-def,union-attr,type-arg"
import os.path
from typing import List, Optional

from textx import get_model

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.node import (
    SDocCompositeNode,
    SDocNode,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.helpers.exception import StrictDocException


class ParseContext:
    def __init__(self, path_to_sdoc_file: Optional[str]):
        self.path_to_sdoc_file: Optional[str] = path_to_sdoc_file
        self.path_to_sdoc_dir: Optional[str] = None
        if path_to_sdoc_file is not None:
            assert os.path.isfile(path_to_sdoc_file), path_to_sdoc_file
            self.path_to_sdoc_dir = os.path.dirname(path_to_sdoc_file)

        self.document_reference: DocumentReference = DocumentReference()
        self.context_document_reference: DocumentReference = DocumentReference()
        self.document_config: Optional[DocumentConfig] = None
        self.document_grammar: DocumentGrammar = DocumentGrammar.create_default(
            None
        )
        self.document_view: Optional[DocumentView] = None
        self.uses_old_refs_field: bool = False
        self.at_least_one_relations_field: bool = False
        self.document_has_requirements = False

        # FIXME: Plain list of all fragments found in the document.
        self.fragments_from_files: List = []


class SDocParsingProcessor:
    def __init__(self, parse_context: ParseContext):
        self.parse_context: ParseContext = parse_context

    def process_document(self, document: SDocDocument):
        document.grammar = self.parse_context.document_grammar
        self.parse_context.document = document
        document.ng_including_document_reference = (
            self.parse_context.context_document_reference
        )

    def get_default_processors(self):
        return {
            "SDocDocument": self.process_document,
            "DocumentConfig": self.process_document_config,
            "DocumentGrammar": self.process_document_grammar,
            "GrammarElement": self.process_document_grammar_element,
            "DocumentView": self.process_document_view,
            "SDocSection": self.process_section,
            "DocumentFromFile": self.process_document_from_file,
            "SDocCompositeNode": self.process_composite_requirement,
            "SDocNode": self.process_requirement,
            "FreeText": self.process_free_text,
        }

    def process_document_config(self, document_config: DocumentConfig):
        the_model = get_model(document_config)
        line_start, col_start = the_model._tx_parser.pos_to_linecol(
            document_config._tx_position
        )
        document_config.ng_line_start = line_start
        document_config.ng_col_start = col_start
        self.parse_context.document_config = document_config

    def process_document_grammar(self, document_grammar: DocumentGrammar):
        self.parse_context.document_grammar = document_grammar

    def process_document_grammar_element(self, grammar_element: GrammarElement):
        the_model = get_model(grammar_element)
        line_start, col_start = the_model._tx_parser.pos_to_linecol(
            grammar_element._tx_position
        )

        if (
            grammar_element.tag == "REQUIREMENT"
            and "STATEMENT" not in grammar_element.fields_map
        ):
            raise StrictDocSemanticError.grammar_missing_reserved_statement(
                grammar_element,
                self.parse_context.path_to_sdoc_file,
                line_start,
                col_start,
            )

    def process_document_view(self, document_view: DocumentView):
        self.parse_context.document_view = document_view

        the_model = get_model(document_view)
        line_start, col_start = the_model._tx_parser.pos_to_linecol(
            document_view._tx_position
        )
        document_view.ng_line_start = line_start
        document_view.ng_col_start = col_start

    def process_section(self, section: SDocSection):
        section.ng_document_reference = self.parse_context.document_reference
        section.ng_including_document_reference = (
            self.parse_context.context_document_reference
        )

        if self.parse_context.document_config.auto_levels:
            if (
                section.ng_resolved_custom_level
                and section.ng_resolved_custom_level != "None"
            ):
                raise StrictDocException(
                    "[SECTION].LEVEL field is provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to On. "
                    f"Section: {section}"
                )
        else:
            if not section.ng_resolved_custom_level:
                raise StrictDocException(
                    "[SECTION].LEVEL field is not provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to Off. "
                    f"Section: {section}"
                )

    def process_document_from_file(self, document_from_file: DocumentFromFile):
        assert isinstance(
            document_from_file, DocumentFromFile
        ), document_from_file

        # Windows paths are backslashes, so using abspath in addition.
        resolved_path_to_fragment_file = os.path.abspath(
            os.path.join(
                self.parse_context.path_to_sdoc_dir, document_from_file.file
            )
        )
        if not os.path.isfile(resolved_path_to_fragment_file):
            raise StrictDocException(
                "[DOCUMENT_FROM_FILE]: Path to a document file does not exist: "
                f"{document_from_file.file}."
            )
        if not resolved_path_to_fragment_file.endswith(".sdoc"):
            raise StrictDocException(
                '[DOCUMENT_FROM_FILE]: A document file name must have ".sdoc" extension: '
                f"{document_from_file.file}."
            )

        document_from_file.ng_document_reference = (
            self.parse_context.document_reference
        )
        document_from_file.resolved_full_path_to_document_file = (
            resolved_path_to_fragment_file
        )

        self.parse_context.current_include_parent = document_from_file.parent
        self.parse_context.fragments_from_files.append(document_from_file)

    def process_composite_requirement(
        self, composite_requirement: SDocCompositeNode
    ):
        self.parse_context.document_has_requirements = True

        if self.parse_context.document_config.auto_levels:
            if composite_requirement.ng_resolved_custom_level:
                raise StrictDocException(
                    "[COMPOSITE_REQUIREMENT].LEVEL field is provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to On. "
                    f"Composite requirement: {composite_requirement}."
                )
        else:
            if not composite_requirement.ng_resolved_custom_level:
                raise StrictDocException(
                    "[COMPOSITE_REQUIREMENT].LEVEL field is not "
                    "provided. This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to Off. "
                    f"Composite requirement: {composite_requirement}."
                )

        composite_requirement.ng_document_reference = (
            self.parse_context.document_reference
        )
        composite_requirement.ng_including_document_reference = (
            self.parse_context.context_document_reference
        )

        cursor = composite_requirement.parent
        while (
            not isinstance(cursor, SDocDocument)
            and not cursor.ng_has_requirements
        ):
            cursor.ng_has_requirements = True
            cursor = cursor.parent

        if (
            composite_requirement.reserved_title is None
            or not self.parse_context.document_config.is_requirement_in_toc()
        ) and self.parse_context.document_config.auto_levels:
            composite_requirement.ng_resolved_custom_level = "None"

    def process_requirement(self, requirement: SDocNode):
        self.parse_context.document_has_requirements = True

        if requirement.ng_uses_old_refs_field:
            self.parse_context.uses_old_refs_field = True
        elif "REFS" in requirement.ordered_fields_lookup:
            self.parse_context.at_least_one_relations_field = True

        if self.parse_context.document_config.auto_levels:
            if requirement.ng_resolved_custom_level:
                raise StrictDocException(
                    "[REQUIREMENT].LEVEL field is provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to On. "
                    f"Requirement: {requirement}."
                )
        else:
            if not requirement.ng_resolved_custom_level:
                raise StrictDocException(
                    "[REQUIREMENT].LEVEL field is not provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to Off. "
                    f"Requirement: {requirement}."
                )

        requirement.ng_document_reference = (
            self.parse_context.document_reference
        )
        requirement.ng_including_document_reference = (
            self.parse_context.context_document_reference
        )

        cursor = requirement.parent
        while (
            not isinstance(cursor, SDocDocument)
            and not cursor.ng_has_requirements
        ):
            cursor.ng_has_requirements = True
            cursor = cursor.parent

        if (
            requirement.reserved_title is None
            or not self.parse_context.document_config.is_requirement_in_toc()
        ) and self.parse_context.document_config.auto_levels:
            requirement.ng_resolved_custom_level = "None"

        """
        Saving the source location information in the requirement object.
        """
        the_model = get_model(requirement)
        line_start, col_start = the_model._tx_parser.pos_to_linecol(
            requirement._tx_position
        )
        line_end, col_end = the_model._tx_parser.pos_to_linecol(
            requirement._tx_position_end
        )
        requirement.ng_line_start = line_start
        requirement.ng_line_end = line_end
        requirement.ng_col_start = col_start
        requirement.ng_col_end = col_end
        requirement.ng_byte_start = requirement._tx_position
        requirement.ng_byte_end = requirement._tx_position_end

    def process_free_text(self, free_text):
        pass
