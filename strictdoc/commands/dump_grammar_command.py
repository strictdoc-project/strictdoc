from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.cli.cli_arg_parser import DumpGrammarCommandConfig


class DumpGrammarCommand:
    @staticmethod
    def execute(config: DumpGrammarCommandConfig) -> None:
        with open(config.output_file, "w", encoding="utf8") as output_file:
            output_file.write(SDocGrammarBuilder.create_raw_grammar())
