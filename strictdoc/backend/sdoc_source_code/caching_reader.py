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
from strictdoc.core.project_config import ProjectConfig


class SourceFileTraceabilityCachingReader:
    @staticmethod
    def read_from_file(
        path_to_file: str, project_config: ProjectConfig
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
            path_to_file, project_config
        )
        try:
            if (
                traceability_info := reader.read_from_file(path_to_file)
            ) is not None:
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
        path_to_file: str, project_config: ProjectConfig
    ) -> Union[
        SourceFileTraceabilityReader,
        SourceFileTraceabilityReader_Python,
        SourceFileTraceabilityReader_C,
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
                return SourceFileTraceabilityReader_C()
        return SourceFileTraceabilityReader()
