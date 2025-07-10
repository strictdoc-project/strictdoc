# mypy: disable-error-code="no-untyped-def"
from typing import Any, Dict, List, Optional, Union

from typing_extensions import TypeAlias

from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode
from strictdoc.core.source_tree import SourceFile
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.file_stats import SourceFileStats

RelationMarkerType: TypeAlias = Union[
    FunctionRangeMarker, LineMarker, RangeMarker, ForwardRangeMarker
]


@auto_described
class SourceFileTraceabilityInfo:
    """
    Class that keeps all traceability info related to a single source file.

    At the init time, only the backward RangeMarkers are available from
    a source file. At runtime, the ForwardRangeMarkers are mixed in
    from the Requirement/FileReference links. This is why the .markers
    is a union.

    Note that g_parts is only used by the textX grammar to allow the
    definition of the child grammar elements. All other instance variables
    of this class are not using or based on g_parts. Instead, they are
    populated during the textX processing step, e.g., via
    general_language_marker_processors.py.
    """

    def __init__(self, g_parts: List[Any]):  # noqa: ARG002
        self.source_file: Optional[SourceFile] = None
        self.source_nodes: List[SourceNode] = []
        self.functions: List[Function] = []

        #
        # {                                              # noqa: ERA001
        #  "REQ-001": [RangeMarker(...), ...],           # noqa: ERA001
        #  "REQ-002": [RangeMarker(...), ...],           # noqa: ERA001
        # }                                              # noqa: ERA001
        self.ng_map_reqs_to_markers: Dict[str, List[RelationMarkerType]] = {}

        self.ng_map_names_to_markers: Dict[str, List[RelationMarkerType]] = {}
        self.ng_map_names_to_definition_functions: Dict[str, Function] = {}

        #
        # Merged ranges contain ranges that are fully covered by one or more
        # forward or backward relations. If a range is part of a larger range,
        # it gets merged into the larger range. The merged ranges are tracked so
        # that for each source code function it can be answered whether the
        # function is covered by any requirement or not.
        #
        self.merged_ranges: List[List[int]] = []
        self.file_stats: SourceFileStats = SourceFileStats()
        self.ng_lines_covered = 0
        self.lines_info: Dict[int, bool] = {}
        self._coverage: float = 0
        self.covered_functions: int = 0

        self.markers: List[RelationMarkerType] = []

    def get_coverage(self):
        return self._coverage

    def set_coverage_stats(
        self,
        merged_ranges: List[List[int]],
        lines_covered: int,
    ) -> None:
        self.merged_ranges = merged_ranges
        self.ng_lines_covered = lines_covered
        self._coverage = (
            round(lines_covered / self.file_stats.lines_non_empty * 100, 1)
            if self.file_stats.lines_non_empty != 0
            else 0
        )
