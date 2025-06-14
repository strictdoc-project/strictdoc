# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import sys
import traceback
from copy import copy
from typing import Any, Tuple

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.constants import DOCUMENT_MODELS
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import (
    SDocCompositeNode,
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.backend.sdoc.processor import ParseContext, SDocParsingProcessor
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.textx import drop_textx_meta


class SDReader:
    meta_model = metamodel_from_str(
        SDocGrammarBuilder.create_grammar(),
        classes=DOCUMENT_MODELS,
        use_regexp_group=True,
    )

    @staticmethod
    def _read(input_string, file_path=None, migrate_sections: bool = False):
        parse_context = ParseContext(
            path_to_sdoc_file=file_path, migrate_sections=migrate_sections
        )
        processor = SDocParsingProcessor(parse_context=parse_context)
        SDReader.meta_model.register_obj_processors(
            processor.get_default_processors()
        )

        document: SDocDocument = SDReader.meta_model.model_from_str(
            input_string, file_name=file_path
        )
        parse_context.document_reference.set_document(document)
        document.ng_has_requirements = parse_context.document_has_requirements

        return document, parse_context

    @staticmethod
    def read(
        input_string, file_path=None, migrate_sections: bool = False
    ) -> SDocDocument:
        document, _ = SDReader.read_with_parse_context(
            input_string, file_path, migrate_sections=migrate_sections
        )
        return document

    @staticmethod
    def read_with_parse_context(
        input_string, file_path=None, migrate_sections: bool = False
    ) -> Tuple[SDocDocument, ParseContext]:
        document, parse_context = SDReader._read(input_string, file_path)

        # FIXME: When the [SECTION] is gone, remove this.
        if migrate_sections:
            SDReader.migrate_sections(document)
            SDReader.migration_sections_grammar(document)
        SDReader.fixup_composite_requirements(document)

        return document, parse_context

    def read_from_file(
        self, file_path: str, project_config: ProjectConfig
    ) -> SDocDocument:
        """
        Parse a provided .sdoc file and convert it into a Document object.
        """

        unpickled_content = PickleCache.read_from_cache(
            file_path, project_config, "sdoc"
        )
        if unpickled_content:
            return assert_cast(unpickled_content, SDocDocument)

        with open(file_path, encoding="utf8") as file:
            sdoc_content = file.read()

        try:
            sdoc, parse_context = self.read_with_parse_context(
                sdoc_content,
                file_path=file_path,
                migrate_sections=project_config.is_new_section_behavior(),
            )

            sdoc.fragments_from_files = parse_context.fragments_from_files

            # HACK:
            # ProcessPoolExecutor doesn't work because of non-picklable parts
            # of textx. The offending fields are stripped down because they
            # are not used anyway.
            drop_textx_meta(sdoc)

            PickleCache.save_to_cache(sdoc, file_path, project_config, "sdoc")

            return sdoc
        except StrictDocException as exception:
            print(f"error: {exception.args[0]}")  # noqa: T201
            sys.exit(1)
        except NotImplementedError:
            traceback.print_exc()
            sys.exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(  # noqa: T201
                f"error: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided.
            traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def convert(section: SDocSection) -> SDocNode:
        fields = []

        if section.mid_permanent:
            fields.append(
                SDocNodeField.create_from_string(
                    None,
                    field_name="MID",
                    field_value=section.reserved_mid,
                    multiline=False,
                )
            )
        if section.reserved_uid is not None:
            fields.append(
                SDocNodeField.create_from_string(
                    None,
                    field_name="UID",
                    field_value=section.reserved_uid,
                    multiline=False,
                )
            )
        if section.ng_resolved_custom_level is not None:
            fields.append(
                SDocNodeField.create_from_string(
                    None,
                    field_name="LEVEL",
                    field_value=section.ng_resolved_custom_level,
                    multiline=False,
                )
            )
        if (
            section.requirement_prefix is not None
            and len(section.requirement_prefix) > 0
        ):
            fields.append(
                SDocNodeField.create_from_string(
                    None,
                    field_name="PREFIX",
                    field_value=section.requirement_prefix,
                    multiline=False,
                )
            )
        fields.append(
            SDocNodeField.create_from_string(
                None,
                field_name="TITLE",
                field_value=section.reserved_title,
                multiline=False,
            )
        )
        node: SDocNode = SDocNode(
            parent=section.parent,
            node_type="SECTION",
            fields=fields,
            relations=[],
            is_composite=True,
            section_contents=section.section_contents,
            node_type_close="SECTION",
        )
        for field_ in fields:
            field_.parent = node

        node.ng_including_document_reference = (
            section.ng_including_document_reference
        )
        node.ng_document_reference = section.ng_document_reference
        node.ng_level = section.ng_level
        node.ng_resolved_custom_level = section.ng_resolved_custom_level
        node.ng_line_start = section.ng_line_start
        node.ng_line_end = section.ng_line_end
        node.ng_col_start = section.ng_col_start
        node.ng_col_end = section.ng_col_end
        node.ng_byte_start = section.ng_byte_start
        node.ng_byte_end = section.ng_byte_end
        return node

    @staticmethod
    def fixup_composite_requirements(sdoc: SDocDocument) -> None:
        for _, node_ in enumerate(copy(sdoc.section_contents)):
            if isinstance(node_, SDocCompositeNode):
                SDReader.migration_sections_grammar(sdoc)
                break

    @staticmethod
    def migrate_sections(sdoc: Any) -> None:
        for node_idx_, node_ in enumerate(copy(sdoc.section_contents)):
            if isinstance(node_, SDocSection):
                SDReader.migrate_sections(node_)

                new_node = SDReader.convert(node_)
                sdoc.section_contents[node_idx_] = new_node

    @staticmethod
    def migration_sections_grammar(sdoc: SDocDocument) -> None:
        grammar: DocumentGrammar = assert_cast(sdoc.grammar, DocumentGrammar)
        section_element_exists = any(
            element_.tag == "SECTION" for element_ in grammar.elements
        )
        if not section_element_exists:
            grammar.update_with_elements(
                [
                    DocumentGrammar.create_default_section_element(
                        grammar, enable_mid=sdoc.config.enable_mid or False
                    )
                ]
                + grammar.elements
            )
