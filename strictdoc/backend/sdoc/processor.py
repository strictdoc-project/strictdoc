# mypy: disable-error-code="arg-type,attr-defined,no-untyped-call,no-untyped-def,union-attr"
import os.path
from typing import List, Optional

from textx import TextXSyntaxError, get_model

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.model import SDocDocumentFromFileIF
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.textx import preserve_source_location_data


class ParseContext:
    def __init__(
        self, path_to_sdoc_file: Optional[str], migrate_sections: bool = False
    ):
        self.path_to_sdoc_file: Optional[str] = path_to_sdoc_file
        self.path_to_sdoc_dir: Optional[str] = None
        if path_to_sdoc_file is not None:
            self.path_to_sdoc_dir = os.path.dirname(path_to_sdoc_file)
        self.document_grammar: Optional[DocumentGrammar] = None
        self.document_reference: DocumentReference = DocumentReference()
        self.context_document_reference: DocumentReference = DocumentReference()
        self.document_config: Optional[DocumentConfig] = None
        self.document_view: Optional[DocumentView] = None
        self.document_has_requirements = False

        self.fragments_from_files: List[SDocDocumentFromFileIF] = []
        self.migrate_sections: bool = migrate_sections


class SDocParsingProcessor:
    def __init__(self, parse_context: ParseContext):
        self.parse_context: ParseContext = parse_context

    def process_document(self, document: SDocDocument):
        document.grammar = (
            self.parse_context.document_grammar
            or DocumentGrammar.create_default(
                document,
                create_section_element=self.parse_context.migrate_sections,
                enable_mid=document.config.enable_mid,
            )
        )
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
            "SDocCompositeNode": self.process_requirement,
            "SDocNode": self.process_requirement,
            "SDocNodeField": self.process_node_field,
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
        preserve_source_location_data(document_grammar)
        # FIXME: It would be great to move forward and remove this.
        if not document_grammar.has_text_element():
            document_grammar.add_element_first(
                DocumentGrammar.create_default_text_element(document_grammar)
            )
        self.parse_context.document_grammar = document_grammar

    def process_document_grammar_element(self, grammar_element: GrammarElement):
        preserve_source_location_data(grammar_element)

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
        preserve_source_location_data(section)
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
        assert isinstance(document_from_file, DocumentFromFile), (
            document_from_file
        )

        # Windows paths are backslashes, so using abspath in addition.
        resolved_path_to_fragment_file = os.path.abspath(
            os.path.join(
                self.parse_context.path_to_sdoc_dir, document_from_file.file
            )
        )
        if not resolved_path_to_fragment_file.endswith(".sdoc"):
            raise StrictDocException(
                '[DOCUMENT_FROM_FILE]: A document file name must have ".sdoc" extension: '
                f"{document_from_file.file}."
            )
        if not os.path.isfile(resolved_path_to_fragment_file):
            raise StrictDocException(
                "[DOCUMENT_FROM_FILE]: Path to a document file does not exist: "
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

    def process_requirement(self, requirement: SDocNode) -> None:
        self.parse_context.document_has_requirements = True

        if self.parse_context.document_config.auto_levels:
            if requirement.ng_resolved_custom_level:
                raise StrictDocException(
                    f"{requirement.get_display_node_type_string()}.LEVEL field is provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to On. "
                    f"Node: {requirement}."
                )
        else:
            if not requirement.ng_resolved_custom_level:
                raise StrictDocException(
                    f"{requirement.get_display_node_type_string()}.LEVEL field is not provided. "
                    "This contradicts to the option "
                    "[DOCUMENT].OPTIONS.AUTO_LEVELS set to Off. "
                    f"Node: {requirement}."
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

        preserve_source_location_data(requirement)

    def process_node_field(self, node_field: SDocNodeField):
        node_field_parts = node_field.parts
        if (
            isinstance(node_field_parts[0], str)
            and node_field_parts[0].strip() == ""
        ):
            the_model = get_model(node_field)
            line_start, col_start = the_model._tx_parser.pos_to_linecol(
                node_field._tx_position
            )
            raise TextXSyntaxError(
                "Node statement cannot be empty.",
                line=line_start,
                col=col_start,
                filename=self.parse_context.path_to_sdoc_file,
            )
