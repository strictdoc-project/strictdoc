import re
from typing import List, Optional, Union

from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    LineMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req

REGEX_REQ = r"[A-Za-z][A-Za-z0-9_\/\.\\-]+"
REGEX_ROLE = r"[A-Za-z][A-Za-z0-9\\-]+"
# @relation(REQ-1, scope=function) or @relation{REQ-1, scope=function}
REGEX_MARKER = re.compile(
    rf"@relation[({{]({REGEX_REQ}(?:, {REGEX_REQ})*), scope=(file|class|function|line|range_start|range_end)(?:, role=({REGEX_ROLE}))?[)}}]"
)


class MarkerParser:
    @staticmethod
    def parse(
        input_string: str,
        line_start: int,
        line_end: int,
        comment_line_start: int,
        comment_column_start: int,
        entity_name: Optional[str] = None,
    ) -> List[Union[FunctionRangeMarker, RangeMarker, LineMarker]]:
        markers: List[Union[FunctionRangeMarker, RangeMarker, LineMarker]] = []
        for input_line_idx_, input_line_ in enumerate(
            input_string.splitlines()
        ):
            match = REGEX_MARKER.search(input_line_)
            if match is None:
                continue

            assert match.lastindex is not None
            marker_type = match.group(2)
            marker_role = match.group(3) if len(match.groups()) >= 3 else None
            req_list = match.group(1)

            first_requirement_index = match.start(1)

            current_line = comment_line_start + input_line_idx_
            first_requirement_column = first_requirement_index + 1
            if input_line_idx_ == 0:
                first_requirement_column += comment_column_start - 1
            requirements = []
            for req_match in re.finditer(REGEX_REQ, req_list):
                req_item = req_match.group(0)  # Matched REQ-XXX item
                # Calculate actual position relative to the original string
                start_index = (
                    req_match.start()
                )  # Offset by where group 1 starts
                requirement = Req(None, req_item)
                requirement.ng_source_line = current_line
                requirement.ng_source_column = (
                    first_requirement_column + start_index
                )
                requirements.append(requirement)

            if marker_type in ("file", "class", "function"):
                function_marker = FunctionRangeMarker(
                    None, requirements, scope=marker_type, role=marker_role
                )
                function_marker.ng_source_line_begin = line_start
                function_marker.ng_range_line_begin = line_start
                function_marker.ng_range_line_end = line_end
                function_marker.ng_marker_line = current_line
                function_marker.ng_marker_column = first_requirement_column
                if marker_type == "file":
                    function_marker.set_description("entire file")
                elif marker_type == "function":
                    function_marker.set_description(f"function {entity_name}()")
                elif marker_type == "class":
                    function_marker.set_description(f"class {entity_name}")
                markers.append(function_marker)
            elif marker_type in ("range_start", "range_end"):
                start_or_end = marker_type == "range_start"
                range_marker = RangeMarker(
                    None,
                    "[" if start_or_end else "[/",
                    requirements,
                    role=marker_role,
                )
                range_marker.ng_source_line_begin = line_start
                range_marker.ng_source_column_begin = first_requirement_column
                range_marker.ng_range_line_begin = line_start
                range_marker.ng_range_line_end = line_end
                range_marker.ng_new_relation_keyword = True
                markers.append(range_marker)
            elif marker_type == "line":
                line_marker = LineMarker(None, requirements, role=marker_role)
                line_marker.ng_source_line_begin = line_start
                line_marker.ng_source_column_begin = first_requirement_column
                line_marker.ng_range_line_begin = line_start
                line_marker.ng_range_line_end = line_end
                markers.append(line_marker)
            else:
                continue

        return markers
