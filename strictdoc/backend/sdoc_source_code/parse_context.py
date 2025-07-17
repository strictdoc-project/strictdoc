"""
@relation(SDOC-SRS-33, scope=file)
"""

from typing import Any, Dict, List, Optional

from strictdoc.backend.sdoc_source_code.models.range_marker import RangeMarker
from strictdoc.helpers.file_stats import SourceFileStats


class ParseContext:
    def __init__(
        self, filename: Optional[str], file_stats: SourceFileStats
    ) -> None:
        self.filename: Optional[str] = filename
        self.file_stats: SourceFileStats = file_stats
        self.markers: List[Any] = []
        self.marker_stack: List[RangeMarker] = []
        self.map_reqs_to_markers: Dict[str, Any] = {}
