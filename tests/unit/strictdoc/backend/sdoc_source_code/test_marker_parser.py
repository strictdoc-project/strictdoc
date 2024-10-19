import sys

import pytest

from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Requires Python 3.9 or higher"
)


def test_01_():
    input_string = """\
@relation(REQ-1, scope=function)
"""

    function_ranges = MarkerParser.parse(input_string, 1, 1, 1, 1)
    function_range = function_ranges[0]
    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 1
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 1
    assert function_range.reqs_objs[0].ng_source_line == 1
    assert function_range.reqs_objs[0].ng_source_column == 11


def test_02_():
    input_string = """\


@relation(REQ-1, scope=function)
"""

    function_ranges = MarkerParser.parse(input_string, 1, 5, 1, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 1
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 3
    assert function_range.reqs_objs[0].ng_source_column == 11


def test_03_():
    input_string = """\


    @relation(REQ-1, scope=function)
"""

    function_ranges = MarkerParser.parse(input_string, 1, 5, 4, 4)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 1
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == (4 - 1) + 3
    assert function_range.reqs_objs[0].ng_source_column == 15


def test_04_():
    input_string = """\
/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
"""

    function_ranges = MarkerParser.parse(input_string, 1, 5, 1, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 1
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14


def test_05_():
    input_string = """\
/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 * @relation(REQ-2, scope=function)
 */
"""

    function_ranges = MarkerParser.parse(input_string, 1, 6, 1, 1)
    function_range = function_ranges[0]

    assert isinstance(function_range, FunctionRangeMarker)
    assert function_range.ng_source_line_begin == 1
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 6
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14
