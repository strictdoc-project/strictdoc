import sys
from typing import List

import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.range_marker import RangeMarker
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_python import (
    SourceFileTraceabilityReader_Python,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Requires Python 3.9 or higher"
)


def test_00_empty_file():
    input_string = b""""""

    reader = SourceFileTraceabilityReader_Python()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_01_single_string():
    input_string = b"""\
# Hello
"""

    reader = SourceFileTraceabilityReader_Python()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.parts) == 0
    assert len(info.markers) == 0


def test_02_functions():
    input_string = b"""\
def hello_1():
    print("1")
    def hello_1_1():
        print("1_1")
        def hello_1_1_1():
            print("1_1_1")
            print("1_1_1 E")
        print("1_1 E")
    print("1 E")
def hello_2():
    print("2")
    def hello_2_1():
        print("2_1")
        def hello_2_1_1():
            print("2_1_1")
            print("2_1_1 E")
        print("2_1 E")
    print("2 E")
def hello_3():
    print("3")
    def hello_3_1():
        print("3_1")
        def hello_3_1_1():
            print("3_1_1")
            print("3_1_1 E")
        print("3_1 E")
    print("3 E")
"""

    reader = SourceFileTraceabilityReader_Python()

    info: SourceFileTraceabilityInfo = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.parts) == 3

    function_1 = info.parts[0]
    assert isinstance(function_1, Function)
    assert function_1.name == "hello_1"
    assert len(function_1.parts) == 1

    function_1_1 = function_1.parts[0]
    assert isinstance(function_1_1, Function)
    assert function_1_1.name == "hello_1_1"
    assert len(function_1_1.parts) == 1

    function_1_1_1 = function_1_1.parts[0]
    assert isinstance(function_1_1_1, Function)
    assert function_1_1_1.name == "hello_1_1_1"
    assert len(function_1_1_1.parts) == 0

    function_2 = info.parts[1]
    assert isinstance(function_2, Function)
    assert function_2.name == "hello_2"
    assert len(function_2.parts) == 1

    function_2_1 = function_2.parts[0]
    assert isinstance(function_2_1, Function)
    assert function_2_1.name == "hello_2_1"
    assert len(function_2_1.parts) == 1

    function_2_1_1 = function_2_1.parts[0]
    assert isinstance(function_2_1_1, Function)
    assert function_2_1_1.name == "hello_2_1_1"
    assert len(function_2_1_1.parts) == 0

    function_3 = info.parts[2]
    assert isinstance(function_3, Function)
    assert function_3.name == "hello_3"
    assert len(function_3.parts) == 1

    function_3_1 = function_3.parts[0]
    assert isinstance(function_3_1, Function)
    assert function_3_1.name == "hello_3_1"
    assert len(function_3_1.parts) == 1

    function_3_1_1 = function_3_1.parts[0]
    assert isinstance(function_3_1_1, Function)
    assert function_3_1_1.name == "hello_3_1_1"
    assert len(function_3_1_1.parts) == 0


def test_001_one_range_marker():
    source_input = b"""
# @relation(REQ-001, REQ-002, REQ-003, scope=range_start)
print("Hello world")
# @relation(REQ-001, REQ-002, REQ-003, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    info: SourceFileTraceabilityInfo = reader.read(source_input)
    markers = info.markers

    assert markers[0].reqs == ["REQ-001", "REQ-002", "REQ-003"]
    assert markers[0].begin_or_end == "["
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 3


def test_002_two_range_markers():
    source_input = b"""
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
# @relation(REQ-002, scope=range_start)
CONTENT 4
CONTENT 5
CONTENT 6
# @relation(REQ-002, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    document = reader.read(source_input)
    markers = document.markers
    assert len(markers) == 4
    marker_1 = markers[0]
    marker_2 = markers[1]
    marker_3 = markers[2]
    marker_4 = markers[3]
    assert marker_1.reqs == ["REQ-001"]
    assert marker_2.reqs == ["REQ-001"]
    assert marker_3.reqs == ["REQ-002"]
    assert marker_4.reqs == ["REQ-002"]

    assert marker_1.ng_source_line_begin == 1
    assert marker_2.ng_source_line_begin == 5
    assert marker_3.ng_source_line_begin == 6
    assert marker_4.ng_source_line_begin == 10

    assert marker_1.ng_range_line_begin == 1
    assert marker_2.ng_range_line_begin == 1
    assert marker_3.ng_range_line_begin == 6
    assert marker_4.ng_range_line_begin == 6


def test_008_three_nested_range_markers():
    source_input = b"""
CONTENT 1
# @relation(REQ-001, scope=range_start)
CONTENT 2
# @relation(REQ-002, scope=range_start)
CONTENT 3
# @relation(REQ-003, scope=range_start)
CONTENT 4
# @relation(REQ-003, scope=range_end)
CONTENT 5
# @relation(REQ-002, scope=range_end)
CONTENT 6
# @relation(REQ-001, scope=range_end)
CONTENT 7
# @relation(REQ-001, scope=range_start)
CONTENT 8
# @relation(REQ-001, scope=range_end)
CONTENT 9
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    document = reader.read(source_input)
    markers = document.markers
    assert len(markers) == 8
    marker_1 = markers[0]
    marker_2 = markers[1]
    marker_3 = markers[2]
    marker_4 = markers[3]
    marker_5 = markers[4]
    marker_6 = markers[5]
    marker_7 = markers[6]
    marker_8 = markers[7]
    assert marker_1.reqs == ["REQ-001"]
    assert marker_2.reqs == ["REQ-002"]
    assert marker_3.reqs == ["REQ-003"]
    assert marker_4.reqs == ["REQ-003"]
    assert marker_5.reqs == ["REQ-002"]
    assert marker_6.reqs == ["REQ-001"]
    assert marker_7.reqs == ["REQ-001"]
    assert marker_8.reqs == ["REQ-001"]

    assert marker_1.ng_source_line_begin == 2
    assert marker_2.ng_source_line_begin == 4
    assert marker_3.ng_source_line_begin == 6
    assert marker_4.ng_source_line_begin == 8
    assert marker_5.ng_source_line_begin == 10
    assert marker_6.ng_source_line_begin == 12
    assert marker_7.ng_source_line_begin == 14
    assert marker_8.ng_source_line_begin == 16

    assert marker_1.ng_range_line_begin == 2
    assert marker_2.ng_range_line_begin == 4
    assert marker_3.ng_range_line_begin == 6
    assert marker_4.ng_range_line_begin == 6
    assert marker_5.ng_range_line_begin == 4
    assert marker_6.ng_range_line_begin == 2
    assert marker_7.ng_range_line_begin == 14
    assert marker_8.ng_range_line_begin == 14


def test_010_nosdoc_keyword():
    source_input = b"""
# @sdoc[nosdoc]
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001]
# @sdoc[/nosdoc]
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    document = reader.read(source_input)
    assert len(document.markers) == 0


def test_011_nosdoc_keyword_then_normal_marker():
    source_input = b"""
# @relation(nosdoc, scope=range_start)
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
# @relation(nosdoc, scope=range_end)
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    document = reader.read(source_input)
    assert len(document.markers) == 2


def test_011_nosdoc_keyword_then_normal_marker_4spaces_indent():
    source_input = b"""
    # @relation(nosdoc, scope=range_start)
    # @relation(REQ-001, scope=range_start)
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # @relation(REQ-001, scope=range_end)
    # @relation(nosdoc, scope=range_end)
    # @relation(REQ-001, scope=range_start)
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # @relation(REQ-001, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    document = reader.read(source_input)
    assert len(document.markers) == 2


# Testing that correct line location is assigned when the marker is not on the
# first line.
def test_012_marker_not_first_line():
    source_input = b"""


# @relation(REQ-001, scope=range_start)
# CONTENT 1
# CONTENT 2
# CONTENT 3
# @relation(REQ-001, scope=range_end)



"""

    reader = SourceFileTraceabilityReader_Python()

    document = reader.read(source_input)

    markers: List[RangeMarker] = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].begin_or_end == "["
    assert markers[0].ng_source_line_begin == 4
    assert markers[0].ng_range_line_begin == 4
    assert markers[0].ng_range_line_end == 8

    assert markers[1].reqs == ["REQ-001"]
    assert markers[1].begin_or_end == "[/"
    assert markers[1].ng_source_line_begin == 8
    assert markers[1].ng_range_line_begin == 4
    assert markers[1].ng_range_line_end == 8


"""
LINE markers.
"""


def test_050_line_marker():
    source_input = b"""
# @relation(REQ-001, scope=line)
CONTENT 1
# @relation(REQ-002, scope=line)
CONTENT 2
# @relation(REQ-003, scope=line)
CONTENT 3
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 1
    assert markers[1].reqs == ["REQ-002"]
    assert markers[1].ng_source_line_begin == 3
    assert markers[1].ng_range_line_begin == 3
    assert markers[1].ng_range_line_end == 3
    assert markers[2].reqs == ["REQ-003"]
    assert markers[2].ng_source_line_begin == 5
    assert markers[2].ng_range_line_begin == 5
    assert markers[2].ng_range_line_end == 5


def test_validation_01_one_range_marker_begin_req_not_equal_to_end_req():
    source_input = b"""
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-002, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "STRICTDOC RANGE: BEGIN and END requirements mismatch"
    )


def test_validation_02_one_range_marker_end_without_begin():
    source_input = b"""
# @relation(REQ-002, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "STRICTDOC RANGE: END marker without preceding BEGIN marker"
    )


def test_validation_03_range_start_without_range_end():
    source_input = b"""
# @relation(REQ-001, scope=range_start)
# @relation(REQ-002, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
""".lstrip()

    reader = SourceFileTraceabilityReader_Python()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "Unmatched @sdoc keyword found in source file."
    )
    assert (
        exc_info.value.args[1]
        == "The @sdoc keywords are also unmatched on lines: [(2, 13)]."
    )
