import re
from typing import List, Union

from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    LineMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req

REGEX_REQ = r"[A-Za-z][A-Za-z0-9\\-]+"
# @relation(REQ-1, scope=function)
REGEX_FUNCTION = (
    rf"@relation\((/?)({REGEX_REQ}(?:, {REGEX_REQ})*)\, scope=function\)"
)
REGEX_RANGE = rf"@sdoc\[(/?)({REGEX_REQ}(?:, {REGEX_REQ})*)\]"
REGEX_LINE = rf"@sdoc\((/?)({REGEX_REQ}(?:, {REGEX_REQ})*)\)"


class MarkerParser:
    @staticmethod
    def parse(
        input_string: str,
        line_start: int,
        line_end: int,
        comment_line_start: int,
        comment_column_start: int,
    ) -> List[Union[FunctionRangeMarker, RangeMarker, LineMarker]]:
        markers: List[Union[FunctionRangeMarker, RangeMarker, LineMarker]] = []
        for input_line_idx_, input_line_ in enumerate(
            input_string.splitlines()
        ):
            match_function = None
            match_line = None
            match_range = None

            match_function = re.search(REGEX_FUNCTION, input_line_)
            if match_function is None:
                match_range = re.search(REGEX_RANGE, input_line_)
                if match_range is None:
                    match_line = re.search(REGEX_LINE, input_line_)

            match = (
                match_function
                if match_function is not None
                else match_range
                if match_range is not None
                else match_line
            )
            if match is None:
                continue

            start_or_end = match.group(1) != "/"
            req_list = match.group(2)

            first_requirement_index = match.start(2)

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

            if match_function is not None:
                function_marker = FunctionRangeMarker(None, requirements)
                function_marker.ng_source_line_begin = line_start
                function_marker.ng_range_line_begin = line_start
                function_marker.ng_range_line_end = line_end
                function_marker.ng_marker_line = current_line
                function_marker.ng_marker_column = first_requirement_column
                markers.append(function_marker)
            elif match_range is not None:
                range_marker = RangeMarker(
                    None, "[" if start_or_end else "[/", requirements
                )
                range_marker.ng_source_line_begin = line_start
                range_marker.ng_source_column_begin = first_requirement_column
                range_marker.ng_range_line_begin = line_start
                range_marker.ng_range_line_end = line_end
                markers.append(range_marker)
            elif match_line is not None:
                line_marker = LineMarker(None, requirements)
                line_marker.ng_source_line_begin = line_start
                line_marker.ng_range_line_begin = line_start
                line_marker.ng_range_line_end = line_end
                markers.append(line_marker)
            else:
                continue

        return markers
