"""
@relation(SDOC-SRS-142, scope=file)
"""

from typing import List

import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.reader import (
    RangeMarker,
    SourceFileTraceabilityReader,
)


def test_001_one_range_marker():
    source_input = """
    # @relation(REQ-001, scope=range_start)
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # @relation(REQ-001, scope=range_end)
    """.lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].is_begin()
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 5

    assert markers[1].reqs == ["REQ-001"]
    assert markers[1].is_end()
    assert markers[1].ng_source_line_begin == 5
    assert markers[1].ng_range_line_begin == 1
    assert markers[1].ng_range_line_end == 5


def test_002_two_range_markers():
    source_input = """
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


def test_003_marker_with_dashes_and_underscores():
    """
    Verifies that SF_REQ-001 markers can be parsed (identifiers with mixed _ and -).

    Bug report: https://github.com/strictdoc-project/strictdoc/discussions/2568.
    """

    source_input = """\
# @relation(SF_REQ-001, scope=file)
CONTENT 1
CONTENT 2
CONTENT 3
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["SF_REQ-001"]
    assert markers[0].is_begin()
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 4


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
# @relation(REQ-001, REQ-002, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, REQ-002, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001", "REQ-002"]
    assert markers[0].is_begin()
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 5

    assert markers[1].reqs == ["REQ-001", "REQ-002"]
    assert markers[1].is_end()
    assert markers[1].ng_source_line_begin == 5
    assert markers[1].ng_range_line_begin == 1
    assert markers[1].ng_range_line_end == 5


def test_010_relation_skip_keyword():
    source_input = """
# @relation(skip, scope=range_start)
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
# @relation(skip, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.g_parts) == 7
    assert len(document.markers) == 0


def test_011_relation_skip_keyword_then_normal_marker():
    source_input = """
# @relation(skip, scope=range_start)
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
# @relation(skip, scope=range_end)
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.g_parts) == 12
    assert len(document.markers) == 2


def test_012_relation_skip_keyword_then_normal_marker_4spaces_indent():
    source_input = """
    # @relation(skip, scope=range_start)
    # @relation(REQ-001, scope=range_start)
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # @relation(REQ-001, scope=range_end)
    # @relation(skip, scope=range_end)
    # @relation(REQ-001, scope=range_start)
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # @relation(REQ-001, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.g_parts) == 12
    assert len(document.markers) == 2


def test_013_relation_skip_entire_file():
    source_input = """\
# @relation(skip, scope=file)
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)
"""

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.g_parts) == 11
    assert len(document.markers) == 0


# Testing that textx assigns correct line location when the marker is not on the
# first line.
def test_020_marker_not_first_line():
    source_input = """


# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-001, scope=range_end)



"""

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)

    markers: List[RangeMarker] = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].is_begin()
    assert markers[0].ng_source_line_begin == 4
    assert markers[0].ng_range_line_begin == 4
    assert markers[0].ng_range_line_end == 8

    assert markers[1].reqs == ["REQ-001"]
    assert markers[1].is_end()
    assert markers[1].ng_source_line_begin == 8
    assert markers[1].ng_range_line_begin == 4
    assert markers[1].ng_range_line_end == 8


def test_031_one_range_marker():
    source_input = """
@relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
@relation(REQ-001, scope=range_end)
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].is_begin()
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 5

    assert markers[1].reqs == ["REQ-001"]
    assert markers[1].is_end()
    assert markers[1].ng_source_line_begin == 5
    assert markers[1].ng_range_line_begin == 1
    assert markers[1].ng_range_line_end == 5


def test_050_line_marker():
    source_input = """
# @relation(REQ-001, scope=line)
CONTENT 1
# @relation(REQ-002, scope=line)
CONTENT 2
# @relation(REQ-003, scope=line)
CONTENT 3
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    markers = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].ng_source_line_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 2
    assert markers[1].reqs == ["REQ-002"]
    assert markers[1].ng_source_line_begin == 3
    assert markers[1].ng_range_line_begin == 3
    assert markers[1].ng_range_line_end == 4
    assert markers[2].reqs == ["REQ-003"]
    assert markers[2].ng_source_line_begin == 5
    assert markers[2].ng_range_line_begin == 5
    assert markers[2].ng_range_line_end == 6


def test_060_file_level_marker():
    source_input = """\
\"\"\"
@relation(REQ-001, scope=file)
\"\"\"

def hello_world():
    pass
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.markers) == 1
    markers = document.markers
    assert markers[0].reqs == ["REQ-001"]
    assert markers[0].ng_source_line_begin == 2
    assert markers[0].ng_source_column_begin == 1
    assert markers[0].ng_range_line_begin == 1
    assert markers[0].ng_range_line_end == 6


def test_validation_01_one_range_marker_begin_req_not_equal_to_end_req():
    source_input = """
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
CONTENT 3
# @relation(REQ-002, scope=range_end)
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
# @relation(REQ-002, scope=range_end)
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
# @relation(REQ-001, scope=range_start)
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
        == "Unmatched @relation keyword found in source file."
    )


def test_validation_04_consecutive_line_markers():
    source_input = """
    # @relation(REQ-001, scope=line)
    # @relation(REQ-002, scope=line)
    """
    reader = SourceFileTraceabilityReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert exc_info.value.args[0] == "Consecutive LineMarkers are not allowed"


def test_validation_05_line_marker_followed_by_eof():
    source_input = "# @relation(REQ-001, scope=line)"

    reader = SourceFileTraceabilityReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(source_input)

    assert exc_info.type is StrictDocSemanticError
    assert exc_info.value.args[0] == "LineMarker cannot be followed by EOF"
