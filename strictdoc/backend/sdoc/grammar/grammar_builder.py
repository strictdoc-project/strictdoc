# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from strictdoc.backend.sdoc.grammar.grammar import (
    DOCUMENT_GRAMMAR,
    FREE_TEXT_PARSER_GRAMMAR,
    SECTION_GRAMMAR,
    TEXT_TYPES_GRAMMAR,
)
from strictdoc.backend.sdoc.grammar.grammar_grammar import GRAMMAR_GRAMMAR
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
            DOCUMENT_GRAMMAR
            + GRAMMAR_GRAMMAR
            + SECTION_GRAMMAR
            + FREE_TEXT_PARSER_GRAMMAR
            + TEXT_TYPES_GRAMMAR
            + STRICTDOC_BASIC_TYPE_SYSTEM
        )
        return grammar

    @staticmethod
    def create_free_text_grammar():
        return SDocGrammarBuilder._prep_grammar(
            FREE_TEXT_PARSER_GRAMMAR + TEXT_TYPES_GRAMMAR
        )

    @staticmethod
    def create_grammar_grammar():
        grammar = SDocGrammarBuilder._prep_grammar(
            GRAMMAR_GRAMMAR + STRICTDOC_BASIC_TYPE_SYSTEM
        )
        return grammar

    @staticmethod
    def create_raw_grammar():
        grammar = (
            DOCUMENT_GRAMMAR
            + GRAMMAR_GRAMMAR
            + SECTION_GRAMMAR
            + FREE_TEXT_PARSER_GRAMMAR
            + TEXT_TYPES_GRAMMAR
            + STRICTDOC_BASIC_TYPE_SYSTEM
        )

        return grammar
