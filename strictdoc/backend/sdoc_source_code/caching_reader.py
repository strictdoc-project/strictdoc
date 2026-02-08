"""
@relation(SDOC-SRS-33, SDOC-SRS-142, scope=file)
"""

from typing import Optional, Union

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
from strictdoc.backend.sdoc_source_code.reader_rust import (
    SourceFileTraceabilityReader_Rust,
)
from strictdoc.core.project_config import ProjectConfig


class SourceFileTraceabilityCachingReader:
    @staticmethod
    def read_from_file(
        path_to_file: str,
        project_config: ProjectConfig,
        source_node_tags: Optional[set[str]] = None,
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
            path_to_file,
            project_config,
            source_node_tags,
        )
        try:
            traceability_info = reader.read_from_file(path_to_file)
            PickleCache.save_to_cache(
                traceability_info,
                path_to_file,
                project_config,
                "source_file",
            )
        except UnicodeDecodeError as error_:
            # Should never reach this point because the binary files should
            # already be filtered out at the FileFinder search step.
            raise error_

        return traceability_info

    @staticmethod
    def _get_reader(
        path_to_file: str,
        project_config: ProjectConfig,
        source_node_tags: Optional[set[str]] = None,
    ) -> Union[
        SourceFileTraceabilityReader,
        SourceFileTraceabilityReader_Python,
        SourceFileTraceabilityReader_C,
        SourceFileTraceabilityReader_Robot,
        SourceFileTraceabilityReader_Rust,
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
                return SourceFileTraceabilityReader_C(
                    custom_tags=source_node_tags
                )
            if path_to_file.endswith(".robot"):
                return SourceFileTraceabilityReader_Robot()
            if path_to_file.endswith(".rs"):
                return SourceFileTraceabilityReader_Rust(
                    custom_tags=source_node_tags
                )
        return SourceFileTraceabilityReader()
