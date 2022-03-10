from textx import metamodel_from_str

from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.free_text import FreeTextContainer
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.processor import ParseContext
from strictdoc.helpers.textx import drop_textx_meta


class SDFreeTextReader:
    @staticmethod
    def _read(input_string, file_path=None):
        meta_model = metamodel_from_str(
            SDocGrammarBuilder.create_free_text_grammar(),
            classes=[FreeTextContainer, InlineLink],
            use_regexp_group=True,
        )

        parse_context = ParseContext()
        # processor = SDocParsingProcessor(
        #     parse_context=parse_context, delegate=SDReader.parse_include
        # )
        # meta_model.register_obj_processors(processor.get_default_processors())

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
        document, _ = SDFreeTextReader._read(input_string, file_path)
        return document
