"""
@relation(SDOC-SRS-33, SDOC-SRS-142, scope=file)
"""

from typing import Optional, Union

from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)
from strictdoc.backend.sdoc_source_code.reader_python import (
    SourceFileTraceabilityReader_Python,
)
from strictdoc.backend.sdoc_source_code.reader_robot import (
    SourceFileTraceabilityReader_Robot,
)
from strictdoc.core.project_config import ProjectConfig


class SourceFileTraceabilityCachingReader:
    @staticmethod
    def read_from_file(
        path_to_file: str,
        project_config: ProjectConfig,
        source_node_grammar_element: Optional[GrammarElement],
    ) -> Optional[SourceFileTraceabilityInfo]:
        unpickled_content = PickleCache.read_from_cache(
            path_to_file, project_config, "source_file"
        )
        if unpickled_content is not None:
            assert isinstance(unpickled_content, SourceFileTraceabilityInfo), (
                path_to_file,
                unpickled_content,
            )
            return unpickled_content

        reader = SourceFileTraceabilityCachingReader._get_reader(
            path_to_file, project_config, source_node_grammar_element
        )
        try:
            traceability_info = reader.read_from_file(path_to_file)
            PickleCache.save_to_cache(
                traceability_info,
                path_to_file,
                project_config,
                "source_file",
            )
        except UnicodeDecodeError:
            print(  # noqa: T201
                f"warning: Skip tracing binary file {path_to_file}."
            )
            return None

        return traceability_info

    @staticmethod
    def _get_reader(
        path_to_file: str,
        project_config: ProjectConfig,
        source_node_grammar_element: Optional[GrammarElement],
    ) -> Union[
        SourceFileTraceabilityReader,
        SourceFileTraceabilityReader_Python,
        SourceFileTraceabilityReader_C,
        SourceFileTraceabilityReader_Robot,
    ]:
        if project_config.is_activated_source_file_language_parsers():
            if path_to_file.endswith(".py"):
                return SourceFileTraceabilityReader_Python()
            if (
                path_to_file.endswith(".c")
                or path_to_file.endswith(".cc")
                or path_to_file.endswith(".h")
                or path_to_file.endswith(".hh")
                or path_to_file.endswith(".hpp")
                or path_to_file.endswith(".cpp")
            ):
                custom_tags = (
                    [
                        field.title
                        for field in source_node_grammar_element.fields
                    ]
                    if source_node_grammar_element is not None
                    else None
                )
                return SourceFileTraceabilityReader_C(custom_tags=custom_tags)
            if path_to_file.endswith(".robot"):
                return SourceFileTraceabilityReader_Robot()
        return SourceFileTraceabilityReader()
