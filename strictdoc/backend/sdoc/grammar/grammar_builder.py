from strictdoc.backend.sdoc.grammar.grammar import (
    STRICTDOC_GRAMMAR,
    STRICTINC_GRAMMAR,
    FREE_TEXT_GRAMMAR,
)
from strictdoc.backend.sdoc.grammar.type_system import (
    STRICTDOC_BASIC_TYPE_SYSTEM,
)


class SDocGrammarBuilder:
    @staticmethod
    def _prep_grammar(grammar):
        grammar = (grammar).replace("'\\n'", "'\n'")
        return grammar

    @staticmethod
    def create_grammar():
        grammar = SDocGrammarBuilder._prep_grammar(
            STRICTDOC_GRAMMAR + STRICTDOC_BASIC_TYPE_SYSTEM
        )
        return grammar

    @staticmethod
    def create_free_text_grammar():
        return SDocGrammarBuilder._prep_grammar(FREE_TEXT_GRAMMAR)

    @staticmethod
    def create_fragment_grammar():
        grammar = SDocGrammarBuilder._prep_grammar(
            STRICTINC_GRAMMAR + STRICTDOC_BASIC_TYPE_SYSTEM
        )
        return grammar

    @staticmethod
    def create_raw_grammar():
        grammar = STRICTDOC_GRAMMAR + STRICTDOC_BASIC_TYPE_SYSTEM
        return grammar
