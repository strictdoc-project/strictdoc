import re
from typing import List, Optional, Union

from strictdoc.backend.sdoc_source_code.helpers.comment_preprocessor import (
    preprocess_source_code_comment,
)
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
    rf"@relation[({{](\s*{REGEX_REQ}(?:,\s+{REGEX_REQ})*),\s+scope=(file|class|function|line|range_start|range_end)(?:,\s+role=({REGEX_ROLE}))?[\s*)}}]"
)


class MarkerParser:
    @staticmethod
    def parse(
        input_string: str,
        line_start: int,
        line_end: int,
        comment_line_start: int,
        entity_name: Optional[str] = None,
    ) -> List[Union[FunctionRangeMarker, RangeMarker, LineMarker]]:
        """
        Parse relation markers from source file comments.

        Before the actual parsing, the function removes all code comment symbols
        such as /** ... */ or /// Doxygen comments or Python

        The line start/end indicate a range where the comment is located in the
        source file.
        The comment_line_start parameter maybe the same as line start but can
        also be different if the comment is part of a Python or C function in
        which case the comment_line_start will be several lines below the actual
        start of the range.
        """

        markers: List[Union[FunctionRangeMarker, RangeMarker, LineMarker]] = []

        input_string = preprocess_source_code_comment(input_string)

        matches = REGEX_MARKER.finditer(input_string)
        for match_ in matches:
            assert match_.lastindex is not None
            marker_type = match_.group(2)
            marker_role = match_.group(3) if len(match_.groups()) >= 3 else None
            req_list = match_.group(1)

            marker_start_index = match_.start(0)

            marker_start_line = comment_line_start + input_string.count(
                "\n", 0, marker_start_index
            )

            marker_line_start_index = input_string.rfind(
                "\n", 0, marker_start_index
            )
            marker_line_start_index = (
                0
                if marker_line_start_index == -1
                else marker_line_start_index + 1
            )

            marker_start_column = (
                marker_start_index - marker_line_start_index
            ) + 1

            all_reqs_start_index = match_.start(1)

            requirements = []
            for req_match in re.finditer(REGEX_REQ, req_list):
                req_start_index = all_reqs_start_index + req_match.start()
                last_newline_pos = input_string.rfind("\n", 0, req_start_index)

                line_start_index = (
                    0 if last_newline_pos == -1 else last_newline_pos + 1
                )

                req_abs_line = comment_line_start + input_string.count(
                    "\n", 0, req_start_index
                )

                first_requirement_index = match_.start(1)
                first_requirement_column = (
                    first_requirement_index - line_start_index
                ) + 1

                req_item = req_match.group(0)

                start_index = req_match.start()
                requirement = Req(None, req_item)
                requirement.ng_source_line = req_abs_line
                requirement.ng_source_column = (
                    first_requirement_column + start_index
                )
                requirements.append(requirement)

            if marker_type in ("file", "class", "function"):
                function_marker = FunctionRangeMarker(
                    None, requirements, scope=marker_type, role=marker_role
                )
                function_marker.ng_source_line_begin = marker_start_line
                function_marker.ng_source_column_begin = marker_start_column
                function_marker.ng_range_line_begin = line_start
                function_marker.ng_range_line_end = line_end
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
                range_marker.ng_source_line_begin = marker_start_line
                range_marker.ng_source_column_begin = marker_start_column
                range_marker.ng_range_line_begin = line_start
                range_marker.ng_range_line_end = line_end
                range_marker.ng_new_relation_keyword = True
                markers.append(range_marker)
            elif marker_type == "line":
                line_marker = LineMarker(None, requirements, role=marker_role)
                line_marker.ng_source_line_begin = marker_start_line
                line_marker.ng_source_column_begin = marker_start_column
                line_marker.ng_range_line_begin = line_start
                line_marker.ng_range_line_end = line_end
                markers.append(line_marker)
            else:
                continue

        return markers
