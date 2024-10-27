from typing import Any, Dict, List

from strictdoc.backend.sdoc_source_code.models.range_marker import RangeMarker


class ParseContext:
    def __init__(self, filename: str, lines_total: int) -> None:
        self.filename: str = filename
        self.lines_total: int = lines_total
        self.markers: List[Any] = []
        self.marker_stack: List[RangeMarker] = []
        self.map_reqs_to_markers: Dict[str, Any] = {}
