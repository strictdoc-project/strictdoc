from strictdoc.backend.sdoc.grammar.grammar import STRICTDOC_GRAMMAR
from strictdoc.backend.sdoc.grammar.type_system import (
    STRICTDOC_BASIC_TYPE_SYSTEM,
)


class SDocGrammarBuilder:
    @staticmethod
    def create_grammar():
        grammar = (STRICTDOC_GRAMMAR + STRICTDOC_BASIC_TYPE_SYSTEM).replace(
            "'\\n'", "'\n'"
        )
        return grammar

    @staticmethod
    def create_raw_grammar():
        grammar = STRICTDOC_GRAMMAR + STRICTDOC_BASIC_TYPE_SYSTEM
        return grammar
