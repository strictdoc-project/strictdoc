import pytest
from strictdoc.backend.dsl.error_handling import StrictDocSemanticError
from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityReader,
)


def test_001_one_range_pragma():
    input = """
# STRICTDOC RANGE BEGIN: REQ-001, REQ-002
CONTENT 1
CONTENT 2
CONTENT 3
# STRICTDOC RANGE END: REQ-001, REQ-002
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(input)
    pragmas = document.pragmas
    assert pragmas[0].reqs == ["REQ-001", "REQ-002"]
    assert pragmas[0].pragma_type == "RANGE"
    assert pragmas[0].begin_or_end == "BEGIN"
    assert pragmas[0].ng_source_line_begin == 1
    assert pragmas[0].ng_source_line_end == 5

    assert pragmas[1].reqs == ["REQ-001", "REQ-002"]
    assert pragmas[1].pragma_type == "RANGE"
    assert pragmas[1].begin_or_end == "END"
    assert pragmas[1].ng_source_line_begin == 5
    assert pragmas[1].ng_source_line_end is None


def test_002_two_range_pragmas():
    input = """
# STRICTDOC RANGE BEGIN: REQ-001
CONTENT 1
CONTENT 2
CONTENT 3
# STRICTDOC RANGE END: REQ-001
# STRICTDOC RANGE BEGIN: REQ-002
CONTENT 4
CONTENT 5
CONTENT 6
# STRICTDOC RANGE END: REQ-002
""".lstrip()

    reader = SourceFileTraceabilityReader()

    document = reader.read(input)
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

    assert pragma_1.ng_source_line_end == 5
    assert pragma_2.ng_source_line_end is None
    assert pragma_3.ng_source_line_end == 10
    assert pragma_4.ng_source_line_end is None


def test_003_one_range_pragma_begin_req_not_equal_to_end_req():
    input = """
# STRICTDOC RANGE BEGIN: REQ-001
CONTENT 1
CONTENT 2
CONTENT 3
# STRICTDOC RANGE END: REQ-002
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
# STRICTDOC RANGE END: REQ-002
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
    traceability_info = reader.read(input)

    print(traceability_info)


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
