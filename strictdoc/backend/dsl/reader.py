import sys
import traceback

from textx import metamodel_from_str

from strictdoc.backend.dsl.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.dsl.error_handling import StrictDocSemanticError
from strictdoc.backend.dsl.models.config_special_field import ConfigSpecialField
from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.inline_link import InlineLink
from strictdoc.backend.dsl.models.reference import (
    Reference,
    ParentReqReference,
    FileReference,
)
from strictdoc.backend.dsl.models.requirement import (
    Requirement,
    CompositeRequirement,
    RequirementComment,
)
from strictdoc.backend.dsl.models.section import Section, FreeText
from strictdoc.backend.dsl.models.special_field import SpecialField
from strictdoc.backend.dsl.processor import SDocParsingProcessor, ParseContext
from strictdoc.helpers.textx import drop_textx_meta

DOCUMENT_MODELS = [
    DocumentConfig,
    ConfigSpecialField,
    Document,
    RequirementComment,
    Section,
    Requirement,
    CompositeRequirement,
    # Body,
    SpecialField,
    Reference,
    ParentReqReference,
    FileReference,
    FreeText,
    InlineLink,
]


class SDReader:
    @staticmethod
    def read(input_string, file_path=None):
        meta_model = metamodel_from_str(
            SDocGrammarBuilder.create_grammar(),
            classes=DOCUMENT_MODELS,
            use_regexp_group=True,
        )

        parse_context = ParseContext()

        processor = SDocParsingProcessor(parse_context=parse_context)

        obj_processors = {
            "Document": processor.process_document,
            "DocumentConfig": processor.process_document_config,
            "Section": processor.process_section,
            "CompositeRequirement": processor.process_composite_requirement,
            "Requirement": processor.process_requirement,
            "FreeText": processor.process_free_text,
        }

        meta_model.register_obj_processors(obj_processors)

        document = meta_model.model_from_str(input_string, file_name=file_path)
        parse_context.document_reference.set_document(document)

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(document)

        return document

    def read_from_file(self, file_path):
        with open(file_path, "r", encoding="utf8") as file:
            sdoc_content = file.read()

        try:
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc
        except NotImplementedError:
            traceback.print_exc()
            sys.exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(
                f"error: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided
            traceback.print_exc()
            sys.exit(1)
