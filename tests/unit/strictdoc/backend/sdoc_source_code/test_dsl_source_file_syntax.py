from typing import List

import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.reader import (
    RangeMarker,
    SourceFileTraceabilityReader,
)


def test_001_one_range_marker():
    source_input = """
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].begin_or_end == "["
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 5

    assert markers[1].reqs == ["REQ-001"]
    assert markers[1].begin_or_end == "[/"
    assert markers[1].ng_source_line_begin == 5
    assert markers[1].ng_range_line_begin == 1
    assert markers[1].ng_range_line_end == 5


def test_002_two_range_markers():
    source_input = """
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001]
# @sdoc[REQ-002]
CONTENT 4
CONTENT 5
CONTENT 6
# @sdoc[/REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

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


def test_005_no_markers():
    source_input = """
def hello_world_2():

    print("hello world")  # noqa: T201
""".lstrip()

    reader = SourceFileTraceabilityReader()
    _ = reader.read(source_input)


def test_006_empty_file():
    source_input = ""

    reader = SourceFileTraceabilityReader()
    traceability_info = reader.read(source_input)

    assert traceability_info.markers == []


def test_007_single_line_with_no_newline():
    source_input = "Single line"

    reader = SourceFileTraceabilityReader()
    traceability_info = reader.read(source_input)

    assert traceability_info.markers == []


def test_008_three_nested_range_markers():
    source_input = """
CONTENT 1
# @sdoc[REQ-001]
CONTENT 2
# @sdoc[REQ-002]
CONTENT 3
# @sdoc[REQ-003]
CONTENT 4
# @sdoc[/REQ-003]
CONTENT 5
# @sdoc[/REQ-002]
CONTENT 6
# @sdoc[/REQ-001]
CONTENT 7
# @sdoc[REQ-001]
CONTENT 8
# @sdoc[/REQ-001]
CONTENT 9
""".lstrip()

    reader = SourceFileTraceabilityReader()

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


def test_009_two_requirements_in_one_marker():
    source_input = """
# @sdoc[REQ-001, REQ-002]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001, REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001", "REQ-002"]
    assert markers[0].begin_or_end == "["
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 5

    assert markers[1].reqs == ["REQ-001", "REQ-002"]
    assert markers[1].begin_or_end == "[/"
    assert markers[1].ng_source_line_begin == 5
    assert markers[1].ng_range_line_begin == 1
    assert markers[1].ng_range_line_end == 5


def test_010_nosdoc_keyword():
    source_input = """
# @sdoc[nosdoc]
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001]
# @sdoc[/nosdoc]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.parts) == 7
    assert len(document.markers) == 0


def test_011_nosdoc_keyword_then_normal_marker():
    source_input = """
# @sdoc[nosdoc]
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001]
# @sdoc[/nosdoc]
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.parts) == 12
    assert len(document.markers) == 2


def test_011_nosdoc_keyword_then_normal_marker_4spaces_indent():
    source_input = """
    # @sdoc[nosdoc]
    # @sdoc[REQ-001]
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # @sdoc[/REQ-001]
    # @sdoc[/nosdoc]
    # @sdoc[REQ-001]
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # @sdoc[/REQ-001]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.parts) == 12
    assert len(document.markers) == 2


# Testing that textx assigns correct line location when the marker is not on the
# first line.
def test_012_marker_not_first_line():
    source_input = """


# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-001]



"""

    reader = SourceFileTraceabilityReader()

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


def test_013_one_range_marker():
    source_input = """
@sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
@sdoc[/REQ-001]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].begin_or_end == "["
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 5

    assert markers[1].reqs == ["REQ-001"]
    assert markers[1].begin_or_end == "[/"
    assert markers[1].ng_source_line_begin == 5
    assert markers[1].ng_range_line_begin == 1
    assert markers[1].ng_range_line_end == 5


def test_050_line_marker():
    source_input = """
# @sdoc(REQ-001)
CONTENT 1
# @sdoc(REQ-002)
CONTENT 2
# @sdoc(REQ-003)
CONTENT 3
""".lstrip()

    reader = SourceFileTraceabilityReader()

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
    source_input = """
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# @sdoc[/REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "STRICTDOC RANGE: BEGIN and END requirements mismatch"
    )


def test_validation_02_one_range_marker_end_without_begin():
    source_input = """
# @sdoc[/REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "STRICTDOC RANGE: END marker without preceding BEGIN marker"
    )


def test_validation_03_range_start_without_range_end():
    source_input = """
# @sdoc[REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
""".lstrip()

    reader = SourceFileTraceabilityReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "Unmatched @sdoc keyword found in source file."
    )
