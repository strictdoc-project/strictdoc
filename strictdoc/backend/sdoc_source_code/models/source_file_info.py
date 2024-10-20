# mypy: disable-error-code="no-untyped-def,type-arg,var-annotated"
from typing import List, Union

from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    LineMarker,
    RangeMarker,
)
from strictdoc.helpers.auto_described import auto_described


@auto_described
class SourceFileTraceabilityInfo:
    def __init__(self, parts: List):
        """
        At the init time, only the backward RangeMarkers are available from
        a source file. At runtime, the ForwardRangeMarkers are mixed in
        from the Requirement/FileReference links. This is why the .markers
        is a union.
        """

        self.parts: List = parts

        """
        {
          2: RangeMarker(...),
          4: RangeMarker(...),
        }
        """
        self.ng_map_lines_to_markers = {}

        """
        {
         "REQ-001": RangeMarker(...),
         "REQ-002": RangeMarker(...),
        }
        """
        self.ng_map_reqs_to_markers = {}

        self.ng_lines_total = 0
        self.ng_lines_covered = 0
        self._coverage = 0
        self.markers: List[
            Union[LineMarker, RangeMarker, ForwardRangeMarker]
        ] = []

    def get_coverage(self):
        return self._coverage

    def set_coverage_stats(self, lines_total, lines_covered):
        self.ng_lines_total = lines_total
        self.ng_lines_covered = lines_covered
        self._coverage = round(lines_covered / lines_total * 100, 1)
