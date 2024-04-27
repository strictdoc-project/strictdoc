# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import sys
import traceback

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.constants import GRAMMAR_MODELS
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.textx import drop_textx_meta


class SDocGrammarReader:
    def __init__(self, path_to_output_root):
        self.path_to_output_root = path_to_output_root

    @staticmethod
    def read(input_string, file_path=None):
        meta_model = metamodel_from_str(
            SDocGrammarBuilder.create_grammar_grammar(),
            classes=GRAMMAR_MODELS,
            use_regexp_group=True,
        )

        grammar = meta_model.model_from_str(input_string, file_name=file_path)

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(grammar)

        return grammar

    def read_from_file(self, file_path):
        unpickled_content = PickleCache.read_from_cache(
            file_path, self.path_to_output_root
        )
        if unpickled_content:
            return assert_cast(unpickled_content, DocumentGrammar)

        with open(file_path, encoding="utf8") as file:
            grammar_content = file.read()

        try:
            grammar = self.read(grammar_content, file_path=file_path)
            PickleCache.save_to_cache(
                grammar, file_path, self.path_to_output_root
            )

            return grammar
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
            # TODO: when --debug is provided
            traceback.print_exc()
            sys.exit(1)
