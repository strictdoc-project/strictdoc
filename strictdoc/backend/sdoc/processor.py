import os.path
from typing import Callable, Dict, List, Optional, Union, cast

from textx import TextXSyntaxError, get_model

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.backend.sdoc.models.model import (
    SDocDocumentFromFileIF,
    SDocDocumentIF,
    SDocNodeIF,
    SDocSectionIF,
)
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.textx import (
    SupportsTxPosition,
    preserve_source_location_data,
)


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
    def __init__(self, parse_context: ParseContext) -> None:
        self.parse_context: ParseContext = parse_context

    def process_document(self, document: SDocDocument) -> None:
        document.grammar = (
            self.parse_context.document_grammar
            or DocumentGrammar.create_default(
                document,
                create_section_element=self.parse_context.migrate_sections,
                enable_mid=document.config.enable_mid or False,
            )
        )
        document.ng_including_document_reference = (
            self.parse_context.context_document_reference
        )

    def get_default_processors(self) -> Dict[str, Callable[..., None]]:
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

    def process_document_config(self, document_config: DocumentConfig) -> None:
        the_model = get_model(document_config)
        line_start, col_start = the_model._tx_parser.pos_to_linecol(
            cast(SupportsTxPosition, document_config)._tx_position
        )
        document_config.ng_line_start = line_start
        document_config.ng_col_start = col_start
        self.parse_context.document_config = document_config

    def process_document_grammar(
        self, document_grammar: DocumentGrammar
    ) -> None:
        assert self.parse_context.document_config is not None

        preserve_source_location_data(document_grammar)
        # FIXME: It would be great to move forward and remove this.
        if not document_grammar.has_text_element():
            document_grammar.add_element_first(
                DocumentGrammar.create_default_text_element(
                    document_grammar,
                    enable_mid=self.parse_context.document_config.enable_mid
                    is True,
                )
            )
        self.parse_context.document_grammar = document_grammar

    def process_document_grammar_element(
        self, grammar_element: GrammarElement
    ) -> None:
        preserve_source_location_data(grammar_element)

    def process_document_view(self, document_view: DocumentView) -> None:
        self.parse_context.document_view = document_view

        the_model = get_model(document_view)
        line_start, col_start = the_model._tx_parser.pos_to_linecol(
            cast(SupportsTxPosition, document_view)._tx_position
        )
        document_view.ng_line_start = line_start
        document_view.ng_col_start = col_start

    def process_section(self, section: SDocSection) -> None:
        section.ng_document_reference = self.parse_context.document_reference
        section.ng_including_document_reference = (
            self.parse_context.context_document_reference
        )
        preserve_source_location_data(section)

        # FIXME: Refactor to eliminate the need in such assert.
        assert self.parse_context.document_config is not None

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

    def process_document_from_file(
        self, document_from_file: DocumentFromFile
    ) -> None:
        assert isinstance(document_from_file, DocumentFromFile), (
            document_from_file
        )

        # Windows paths are backslashes, so using abspath in addition.
        assert self.parse_context.path_to_sdoc_dir is not None
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

        self.parse_context.fragments_from_files.append(document_from_file)

    def process_requirement(self, requirement: SDocNode) -> None:
        self.parse_context.document_has_requirements = True

        requirement.ng_document_reference = (
            self.parse_context.document_reference
        )
        requirement.ng_including_document_reference = (
            self.parse_context.context_document_reference
        )

        cursor: Union[SDocDocumentIF, SDocSectionIF, SDocNodeIF] = (
            requirement.parent
        )
        while (
            isinstance(cursor, (SDocSectionIF, SDocNodeIF))
            and not cursor.ng_has_requirements
        ):
            cursor.ng_has_requirements = True
            cursor = cursor.parent

        assert self.parse_context.document_config is not None
        if (
            requirement.reserved_title is None
            or not self.parse_context.document_config.is_requirement_in_toc()
        ) and self.parse_context.document_config.auto_levels:
            requirement.ng_resolved_custom_level = "None"

        preserve_source_location_data(requirement)

    def process_node_field(self, node_field: SDocNodeField) -> None:
        node_field_parts = node_field.parts
        if (
            isinstance(node_field_parts[0], str)
            and node_field_parts[0].strip() == ""
        ):
            the_model = get_model(node_field)
            line_start, col_start = the_model._tx_parser.pos_to_linecol(
                cast(SupportsTxPosition, node_field)._tx_position
            )
            raise TextXSyntaxError(
                "Node statement cannot be empty.",
                line=line_start,
                col=col_start,
                filename=self.parse_context.path_to_sdoc_file,
            )
