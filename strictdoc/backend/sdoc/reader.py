import sys
import traceback

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.include_reader import SDIncludeReader
from strictdoc.backend.sdoc.models.constants import DOCUMENT_MODELS
from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.backend.sdoc.processor import SDocParsingProcessor, ParseContext
from strictdoc.helpers.textx import drop_textx_meta


class SDReader:
    @staticmethod
    def _read(input_string, file_path=None):
        meta_model = metamodel_from_str(
            SDocGrammarBuilder.create_grammar(),
            classes=DOCUMENT_MODELS,
            use_regexp_group=True,
        )

        parse_context = ParseContext()
        processor = SDocParsingProcessor(
            parse_context=parse_context, delegate=SDReader.parse_include
        )
        meta_model.register_obj_processors(processor.get_default_processors())

        document = meta_model.model_from_str(input_string, file_name=file_path)
        parse_context.document_reference.set_document(document)

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(document)

        return document, parse_context

    @staticmethod
    def read(input_string, file_path=None):
        document, _ = SDReader._read(input_string, file_path)
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

    @staticmethod
    def parse_include(include, parse_context):
        reader = SDIncludeReader()
        fragment = reader.read_from_file(
            file_path=include.file, context=parse_context
        )
        assert isinstance(fragment, Fragment)
        return fragment
