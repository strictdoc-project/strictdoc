import threading
from typing import ClassVar, Optional

from textx import metamodel_from_str
from textx.metamodel import TextXMetaModel

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
    # All readers share one metamodel, which is built on the first parse, not
    # at import time. Every export imports this module. On an export without
    # changes, all grammars come from the cache, and nothing is parsed. A
    # build at import time would add about 20 ms to such an export.
    #
    # The lock lets only one thread at a time build the metamodel, as the
    # import lock of Python did before. textX is not thread-safe while it
    # builds a metamodel, see SourceFileTraceabilityReader.
    _meta_model: ClassVar[Optional[TextXMetaModel]] = None
    _meta_model_lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def _get_meta_model() -> TextXMetaModel:
        with SDocGrammarReader._meta_model_lock:
            if SDocGrammarReader._meta_model is None:
                SDocGrammarReader._meta_model = metamodel_from_str(
                    SDocGrammarBuilder.create_grammar_grammar(),
                    classes=GRAMMAR_MODELS + [DocumentGrammarWrapper],
                    use_regexp_group=True,
                )
            return SDocGrammarReader._meta_model

    @staticmethod
    def read(
        input_string: str, file_path: Optional[str] = None
    ) -> DocumentGrammar:
        meta_model = SDocGrammarReader._get_meta_model()
        meta_model.register_obj_processors(
            {
                "GrammarElement": preserve_source_location_data,
            }
        )

        try:
            grammar_wrapper: DocumentGrammarWrapper = meta_model.model_from_str(
                input_string, file_name=file_path
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

    @staticmethod
    def read_from_cache(
        file_path: str, project_config: ProjectConfig
    ) -> Optional[DocumentGrammar]:
        """
        Return the grammar from the cache, or None if the cache has no
        up-to-date entry for the file.
        """
        cached_content: Optional[DocumentGrammar] = assert_optional_cast(
            PickleCache.read_from_cache(file_path, project_config, "grammar"),
            DocumentGrammar,
        )
        return cached_content

    def read_from_file(
        self, file_path: str, project_config: ProjectConfig
    ) -> DocumentGrammar:
        cached_grammar = SDocGrammarReader.read_from_cache(
            file_path, project_config
        )
        if cached_grammar is not None:
            return cached_grammar

        with file_open_read_utf8(file_path) as file:
            grammar_content = file.read()

        grammar: DocumentGrammar = self.read(
            grammar_content, file_path=file_path
        )
        PickleCache.save_to_cache(grammar, file_path, project_config, "grammar")

        return grammar
