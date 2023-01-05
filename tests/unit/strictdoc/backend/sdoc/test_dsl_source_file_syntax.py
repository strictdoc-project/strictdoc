from typing import List

import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityReader,
    RangePragma,
)


def test_001_one_range_pragma():
    input = """
# [REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-001]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(input)
    pragmas = document.pragmas
    assert pragmas[0].reqs == ["REQ-001"]
    assert pragmas[0].begin_or_end == "["
    assert pragmas[0].ng_source_line_begin == 1
    assert pragmas[0].ng_range_line_begin == 1
    assert pragmas[0].ng_range_line_end == 5

    assert pragmas[1].reqs == ["REQ-001"]
    assert pragmas[1].begin_or_end == "[/"
    assert pragmas[1].ng_source_line_begin == 5
    assert pragmas[1].ng_range_line_begin == 1
    assert pragmas[1].ng_range_line_end == 5

    assert document._ng_lines_total == 5
    assert document._ng_lines_covered == 5
    assert document.get_coverage() == 100


def test_002_two_range_pragmas():
    source_input = """
# [REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-001]
# [REQ-002]
CONTENT 4
CONTENT 5
CONTENT 6
# [/REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    pragmas = document.pragmas
    assert len(pragmas) == 4
    pragma_1 = pragmas[0]
    pragma_2 = pragmas[1]
    pragma_3 = pragmas[2]
    pragma_4 = pragmas[3]
    assert pragma_1.reqs == ["REQ-001"]
    assert pragma_2.reqs == ["REQ-001"]
    assert pragma_3.reqs == ["REQ-002"]
    assert pragma_4.reqs == ["REQ-002"]

    assert pragma_1.ng_source_line_begin == 1
    assert pragma_2.ng_source_line_begin == 5
    assert pragma_3.ng_source_line_begin == 6
    assert pragma_4.ng_source_line_begin == 10

    assert pragma_1.ng_range_line_begin == 1
    assert pragma_2.ng_range_line_begin == 1
    assert pragma_3.ng_range_line_begin == 6
    assert pragma_4.ng_range_line_begin == 6


def test_003_one_range_pragma_begin_req_not_equal_to_end_req():
    input = """
# [REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "STRICTDOC RANGE: BEGIN and END requirements mismatch"
    )


def test_004_one_range_pragma_end_without_begin():
    input = """
# [/REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input)

    assert exc_info.type is StrictDocSemanticError
    assert (
        exc_info.value.args[0]
        == "STRICTDOC RANGE: END pragma without preceding BEGIN pragma"
    )


def test_005_no_pragmas():
    input = """
def hello_world_2():

    print("hello world")
""".lstrip()

    reader = SourceFileTraceabilityReader()
    _ = reader.read(input)


def test_006_empty_file():
    input = ""

    reader = SourceFileTraceabilityReader()
    traceability_info = reader.read(input)

    assert traceability_info.pragmas == []


def test_007_single_line_with_no_newline():
    input = "Single line"

    reader = SourceFileTraceabilityReader()
    traceability_info = reader.read(input)

    assert traceability_info.pragmas == []


def test_008_three_nested_range_pragmas():
    source_input = """
CONTENT 1
# [REQ-001]
CONTENT 2
# [REQ-002]
CONTENT 3
# [REQ-003]
CONTENT 4
# [/REQ-003]
CONTENT 5
# [/REQ-002]
CONTENT 6
# [/REQ-001]
CONTENT 7
# [REQ-001]
CONTENT 8
# [/REQ-001]
CONTENT 9
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    pragmas = document.pragmas
    assert len(pragmas) == 8
    pragma_1 = pragmas[0]
    pragma_2 = pragmas[1]
    pragma_3 = pragmas[2]
    pragma_4 = pragmas[3]
    pragma_5 = pragmas[4]
    pragma_6 = pragmas[5]
    pragma_7 = pragmas[6]
    pragma_8 = pragmas[7]
    assert pragma_1.reqs == ["REQ-001"]
    assert pragma_2.reqs == ["REQ-002"]
    assert pragma_3.reqs == ["REQ-003"]
    assert pragma_4.reqs == ["REQ-003"]
    assert pragma_5.reqs == ["REQ-002"]
    assert pragma_6.reqs == ["REQ-001"]
    assert pragma_7.reqs == ["REQ-001"]
    assert pragma_8.reqs == ["REQ-001"]

    assert pragma_1.ng_source_line_begin == 2
    assert pragma_2.ng_source_line_begin == 4
    assert pragma_3.ng_source_line_begin == 6
    assert pragma_4.ng_source_line_begin == 8
    assert pragma_5.ng_source_line_begin == 10
    assert pragma_6.ng_source_line_begin == 12
    assert pragma_7.ng_source_line_begin == 14
    assert pragma_8.ng_source_line_begin == 16

    assert pragma_1.ng_range_line_begin == 2
    assert pragma_2.ng_range_line_begin == 4
    assert pragma_3.ng_range_line_begin == 6
    assert pragma_4.ng_range_line_begin == 6
    assert pragma_5.ng_range_line_begin == 4
    assert pragma_6.ng_range_line_begin == 2
    assert pragma_7.ng_range_line_begin == 14
    assert pragma_8.ng_range_line_begin == 14

    assert document._ng_lines_total == 17
    assert document._ng_lines_covered == 14
    assert document.get_coverage() == 82.4


def test_009_two_requirements_in_one_pragma():
    source_input = """
# [REQ-001, REQ-002]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-001, REQ-002]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    pragmas = document.pragmas
    assert pragmas[0].reqs == ["REQ-001", "REQ-002"]
    assert pragmas[0].begin_or_end == "["
    assert pragmas[0].ng_source_line_begin == 1
    assert pragmas[0].ng_range_line_begin == 1
    assert pragmas[0].ng_range_line_end == 5

    assert pragmas[1].reqs == ["REQ-001", "REQ-002"]
    assert pragmas[1].begin_or_end == "[/"
    assert pragmas[1].ng_source_line_begin == 5
    assert pragmas[1].ng_range_line_begin == 1
    assert pragmas[1].ng_range_line_end == 5

    assert document._ng_lines_total == 5
    assert document._ng_lines_covered == 5
    assert document.get_coverage() == 100


def test_010_nosdoc_keyword():
    source_input = """
# [nosdoc]
# [REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-001]
# [/nosdoc]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.parts) == 1
    assert len(document.pragmas) == 0


def test_011_nosdoc_keyword_then_normal_pragma():
    source_input = """
# [nosdoc]
# [REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-001]
# [/nosdoc]
# [REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-001]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)
    assert len(document.parts) == 6
    assert len(document.pragmas) == 2


def test_011_nosdoc_keyword_then_normal_pragma_4spaces_indent():
    input = """
    # [nosdoc]
    # [REQ-001]
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # [/REQ-001]
    # [/nosdoc]
    # [REQ-001]
    CONTENT 1
    CONTENT 2
    CONTENT 3
    # [/REQ-001]
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(input)
    assert len(document.parts) == 6
    assert len(document.pragmas) == 2


# Testing that textx assigns correct line location when the pragma is not on the
# first line.
def test_012_pragma_not_first_line():
    source_input = """


# [REQ-001]
CONTENT 1
CONTENT 2
CONTENT 3
# [/REQ-001]



"""

    reader = SourceFileTraceabilityReader()

    document = reader.read(source_input)

    pragmas: List[RangePragma] = document.pragmas
    assert pragmas[0].reqs == ["REQ-001"]
    assert pragmas[0].begin_or_end == "["
    assert pragmas[0].ng_source_line_begin == 4
    assert pragmas[0].ng_range_line_begin == 4
    assert pragmas[0].ng_range_line_end == 8

    assert pragmas[1].reqs == ["REQ-001"]
    assert pragmas[1].begin_or_end == "[/"
    assert pragmas[1].ng_source_line_begin == 8
    assert pragmas[1].ng_range_line_begin == 4
    assert pragmas[1].ng_range_line_end == 8

    assert document._ng_lines_total == 11
    assert document._ng_lines_covered == 5
    assert document.get_coverage() == 45.5
