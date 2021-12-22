from strictdoc.backend.dsl.grammar.grammar import STRICTDOC_GRAMMAR
from strictdoc.backend.dsl.grammar.type_system import STRICTDOC_BASIC_TYPE_SYSTEM


class SDocGrammarBuilder:
    @staticmethod
    def create_grammar():
        return (
            STRICTDOC_GRAMMAR + STRICTDOC_BASIC_TYPE_SYSTEM
        )
