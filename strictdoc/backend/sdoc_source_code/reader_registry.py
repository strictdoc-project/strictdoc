from typing import TYPE_CHECKING, Optional, Union

from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.core.project_config import ProjectConfig

# Each language reader loads its own parser (tree-sitter grammars, Robot
# Framework, Lark). get_reader() imports a reader only when a file of its
# language is read, so that a project pays only for the languages it has.
if TYPE_CHECKING:
    from strictdoc.backend.sdoc_source_code.reader_ada import (
        SourceFileTraceabilityReader_Ada,
    )
    from strictdoc.backend.sdoc_source_code.reader_c import (
        SourceFileTraceabilityReader_C,
    )
    from strictdoc.backend.sdoc_source_code.reader_modelica import (
        SourceFileTraceabilityReader_Modelica,
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


class SourceCodeReaderRegistry:
    @staticmethod
    def get_reader(
        path_to_file: str,
        project_config: ProjectConfig,  # noqa: ARG004
        source_node_tags: Optional[set[str]] = None,
    ) -> Union[
        SourceFileTraceabilityReader,
        "SourceFileTraceabilityReader_Python",
        "SourceFileTraceabilityReader_C",
        "SourceFileTraceabilityReader_Robot",
        "SourceFileTraceabilityReader_Rust",
        "SourceFileTraceabilityReader_Ada",
        "SourceFileTraceabilityReader_Modelica",
    ]:
        if path_to_file.endswith(".py"):
            from strictdoc.backend.sdoc_source_code.reader_python import (  # noqa: PLC0415
                SourceFileTraceabilityReader_Python,
            )

            return SourceFileTraceabilityReader_Python()
        if (
            path_to_file.endswith(".c")
            or path_to_file.endswith(".cc")
            or path_to_file.endswith(".h")
            or path_to_file.endswith(".hh")
            or path_to_file.endswith(".hpp")
            or path_to_file.endswith(".cpp")
        ):
            from strictdoc.backend.sdoc_source_code.reader_c import (  # noqa: PLC0415
                SourceFileTraceabilityReader_C,
            )

            return SourceFileTraceabilityReader_C(custom_tags=source_node_tags)
        if path_to_file.endswith(".robot"):
            from strictdoc.backend.sdoc_source_code.reader_robot import (  # noqa: PLC0415
                SourceFileTraceabilityReader_Robot,
            )

            return SourceFileTraceabilityReader_Robot(
                custom_tags=source_node_tags
            )
        if path_to_file.endswith(".rs"):
            from strictdoc.backend.sdoc_source_code.reader_rust import (  # noqa: PLC0415
                SourceFileTraceabilityReader_Rust,
            )

            return SourceFileTraceabilityReader_Rust(
                custom_tags=source_node_tags
            )
        if path_to_file.endswith((".adb", ".ads", ".ada")):
            from strictdoc.backend.sdoc_source_code.reader_ada import (  # noqa: PLC0415
                SourceFileTraceabilityReader_Ada,
            )

            return SourceFileTraceabilityReader_Ada(
                custom_tags=source_node_tags
            )
        if path_to_file.endswith(".mo"):
            from strictdoc.backend.sdoc_source_code.reader_modelica import (  # noqa: PLC0415
                SourceFileTraceabilityReader_Modelica,
            )

            return SourceFileTraceabilityReader_Modelica()
        return SourceFileTraceabilityReader()
