"""
@relation(SDOC-SRS-33, scope=file)
"""

from typing import Any, Dict, List, Optional, Union

from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import RangeMarker
from strictdoc.helpers.file_stats import SourceFileStats


class ParseContext:
    def __init__(
        self, filename: Optional[str], file_stats: SourceFileStats
    ) -> None:
        self.filename: str = filename if filename else "<no filename>"
        self.file_stats: SourceFileStats = file_stats
        self.markers: List[Any] = []
        self.marker_stack: List[
            Union[RangeMarker, FunctionRangeMarker, LineMarker]
        ] = []
        self.map_reqs_to_markers: Dict[str, Any] = {}
