import sys

import pytest

from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Requires Python 3.9 or higher"
)


def test_01_basic_nominal():
    input_strings = [
        "@relation(REQ-1, scope=function)\n",
        "@relation(REQ_1, scope=function)\n",
        "@relation(REQ.1, scope=function)\n",
        "@relation(REQ/1, scope=function)\n",
    ]

    for input_string_ in input_strings:
        function_ranges = MarkerParser.parse(input_string_, 1, 1, 1)
        function_range = function_ranges[0]
        assert isinstance(function_range, FunctionRangeMarker)
        assert function_range.ng_source_line_begin == 1
        assert function_range.ng_range_line_begin == 1
        assert function_range.ng_range_line_end == 1
        assert function_range.reqs_objs[0].ng_source_line == 1
        assert function_range.reqs_objs[0].ng_source_column == 11


def test_10_parses_with_leading_newlines():
    input_string = """\


@relation(REQ-1, scope=function)
"""

    function_ranges = MarkerParser.parse(input_string, 1, 5, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 3
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 3
    assert function_range.reqs_objs[0].ng_source_column == 11


def test_11_parses_with_leading_whitespace():
    input_string = """\


    @relation(REQ-1, scope=function)
"""

    function_ranges = MarkerParser.parse(input_string, 1, 3, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 3
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 3
    assert function_range.reqs_objs[0].ng_source_line == 3
    assert function_range.reqs_objs[0].ng_source_column == 15


def test_20_parses_within_doxygen_comment():
    input_string = """\
/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
"""

    function_ranges = MarkerParser.parse(input_string, 1, 5, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14


def test_21_parses_within_doxygen_comment_two_markers():
    input_string = """\
/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 * @relation(REQ-2, scope=function)
 */
"""

    function_ranges = MarkerParser.parse(input_string, 1, 6, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 6
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14


def test_22_parses_within_doxygen_comment_curly_braces():
    input_string = """\
/**
 * Some text.
 *
 * @relation{REQ-1, scope=function}
 */
"""

    function_ranges = MarkerParser.parse(input_string, 1, 5, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14


def test_23_parses_within_doxygen_comment():
    input_string = """\
/**
 * Some text.
 *
 * @relation(
 *     REQ-1,
 *     REQ-2,
 *     REQ-3,
 *     scope=function
 * )
 * @relation(
 *     REQ-4,
 *     REQ-5,
 *     REQ-6,
 *     scope=function
 * )
 */
"""

    function_ranges = MarkerParser.parse(input_string, 1, 16, 1)

    function_range = function_ranges[0]
    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 16
    assert function_range.reqs_objs[0].uid == "REQ-1"
    assert function_range.reqs_objs[0].ng_source_line == 5
    assert function_range.reqs_objs[0].ng_source_column == 8
    assert function_range.reqs_objs[1].uid == "REQ-2"
    assert function_range.reqs_objs[1].ng_source_line == 6
    assert function_range.reqs_objs[1].ng_source_column == 8
    assert function_range.reqs_objs[2].uid == "REQ-3"
    assert function_range.reqs_objs[2].ng_source_line == 7
    assert function_range.reqs_objs[2].ng_source_column == 8

    function_range = function_ranges[1]
    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 10
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 16
    assert function_range.reqs_objs[0].uid == "REQ-4"
    assert function_range.reqs_objs[0].ng_source_line == 11
    assert function_range.reqs_objs[0].ng_source_column == 8
    assert function_range.reqs_objs[1].uid == "REQ-5"
    assert function_range.reqs_objs[1].ng_source_line == 12
    assert function_range.reqs_objs[1].ng_source_column == 8
    assert function_range.reqs_objs[2].uid == "REQ-6"
    assert function_range.reqs_objs[2].ng_source_line == 13
    assert function_range.reqs_objs[2].ng_source_column == 8
