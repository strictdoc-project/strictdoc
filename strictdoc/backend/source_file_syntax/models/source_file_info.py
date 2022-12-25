from typing import List

from strictdoc.backend.source_file_syntax.models.range_pragma import RangePragma
from strictdoc.helpers.auto_described import auto_described


@auto_described
class SourceFileTraceabilityInfo:
    def __init__(self, parts):
        self.parts = parts
        self.ng_map_lines_to_pragmas = {}
        self.ng_map_reqs_to_pragmas = {}

        self._ng_lines_total = 0
        self._ng_lines_covered = 0
        self._coverage = 0
        self.pragmas: List[RangePragma] = []

    def get_coverage(self):
        return self._coverage

    def set_coverage_stats(self, lines_total, lines_covered):
        self._ng_lines_total = lines_total
        self._ng_lines_covered = lines_covered
        self._coverage = round(lines_covered / lines_total * 100, 1)
