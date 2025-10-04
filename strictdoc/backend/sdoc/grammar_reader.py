from typing import Optional

from textx import metamodel_from_str

from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.constants import GRAMMAR_MODELS
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    DocumentGrammarWrapper,
)
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_optional_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_system import file_open_read_utf8
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

        try:
            grammar_wrapper: DocumentGrammarWrapper = (
                SDocGrammarReader.meta_model.model_from_str(
                    input_string, file_name=file_path
                )
            )
        except Exception as exc_:  # pylint: disable=broad-except
            raise StrictDocException(
                f"Could not parse file: "
                f"{file_path}. "
                f"Error: {exc_.__class__.__name__}: {exc_}"
            ) from exc_

        grammar: DocumentGrammar = grammar_wrapper.grammar
        grammar.parent = None

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

        with file_open_read_utf8(file_path) as file:
            grammar_content = file.read()

        grammar: DocumentGrammar = self.read(
            grammar_content, file_path=file_path
        )
        PickleCache.save_to_cache(grammar, file_path, project_config, "grammar")

        return grammar
