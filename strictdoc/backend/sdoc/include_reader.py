import sys
import traceback

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.constants import INCLUDE_MODELS
from strictdoc.backend.sdoc.processor import ParseContext, SDocParsingProcessor
from strictdoc.helpers.textx import drop_textx_meta


class SDIncludeReader:
    @staticmethod
    def read(input_string, parse_context: ParseContext, file_path=None):
        meta_model = metamodel_from_str(
            SDocGrammarBuilder.create_fragment_grammar(),
            classes=INCLUDE_MODELS,
            use_regexp_group=True,
        )
        assert isinstance(parse_context, ParseContext)

        processor = SDocParsingProcessor(
            parse_context=parse_context, delegate=None
        )
        meta_model.register_obj_processors(processor.get_default_processors())

        section = meta_model.model_from_str(input_string, file_name=file_path)

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(section)

        return section

    def read_from_file(self, file_path, context: ParseContext):
        with open(file_path, "r", encoding="utf8") as file:
            ssec_content = file.read()

        try:
            ssec = self.read(ssec_content, context, file_path=file_path)
            return ssec
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
