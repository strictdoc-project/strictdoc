import sys
import traceback
from typing import Optional

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.constants import GRAMMAR_MODELS
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    DocumentGrammarWrapper,
)
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_optional_cast
from strictdoc.helpers.textx import (
    drop_textx_meta,
    preserve_source_location_data,
)


class SDocGrammarReader:
    meta_model = metamodel_from_str(
        SDocGrammarBuilder.create_grammar_grammar(),
        classes=GRAMMAR_MODELS + [DocumentGrammarWrapper],
        use_regexp_group=True,
    )

    @staticmethod
    def read(
        input_string: str, file_path: Optional[str] = None
    ) -> DocumentGrammar:
        SDocGrammarReader.meta_model.register_obj_processors(
            {
                "GrammarElement": preserve_source_location_data,
            }
        )

        grammar_wrapper: DocumentGrammarWrapper = (
            SDocGrammarReader.meta_model.model_from_str(
                input_string, file_name=file_path
            )
        )
        grammar: DocumentGrammar = grammar_wrapper.grammar
        grammar.parent = None

        if not grammar.has_text_element():
            grammar.add_element_first(
                DocumentGrammar.create_default_text_element(grammar)
            )

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(grammar)

        return grammar

    def read_from_file(
        self, file_path: str, project_config: ProjectConfig
    ) -> DocumentGrammar:
        unpickled_content: Optional[DocumentGrammar] = assert_optional_cast(
            PickleCache.read_from_cache(file_path, project_config, "grammar"),
            DocumentGrammar,
        )
        if unpickled_content is not None:
            return unpickled_content

        with open(file_path, encoding="utf8") as file:
            grammar_content = file.read()

        try:
            grammar: DocumentGrammar = self.read(
                grammar_content, file_path=file_path
            )
            PickleCache.save_to_cache(
                grammar, file_path, project_config, "grammar"
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
            # TODO: when --debug is provided.
            traceback.print_exc()
            sys.exit(1)
