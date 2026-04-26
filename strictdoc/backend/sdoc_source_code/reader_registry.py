from typing import Optional, Union

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


class SourceCodeReaderRegistry:
    @staticmethod
    def get_reader(
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
