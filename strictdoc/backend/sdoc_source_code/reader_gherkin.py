import sys

from gherkin import Compiler, Parser

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    source_file_traceability_info_processor,
)
from strictdoc.helpers.file_stats import SourceFileStats


class SourceFileTraceabilityReader_Gherkin:
    def read(
        self, input_buffer: str, file_path: str
    ) -> SourceFileTraceabilityInfo:
        traceability_info = SourceFileTraceabilityInfo([])
        if len(input_buffer) == 0:
            return traceability_info
        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)

        gherkin_document = Parser().parse(input_buffer)


        # gherkin_document["uri"] = "uri_of_the_feature.feature"
        # pickles = Compiler().compile(gherkin_document)

        assert 0, gherkin_document
        assert 0
        source_file_traceability_info_processor(
            traceability_info, parse_context
        )
        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        try:
            with open(file_path) as file:
                sdoc_content = file.read()
                sdoc = self.read(sdoc_content, file_path=file_path)
                return sdoc
        except UnicodeDecodeError:
            raise
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(  # noqa: T201
                f"error: SourceFileTraceabilityReader_Robot: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided
            # traceback.print_exc()  # noqa: ERA001
            sys.exit(1)
