import sys

import pytest

from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Requires Python 3.9 or higher"
)


def test_00_empty_file():
    input_string = b""""""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_01_single_string():
    input_string = b"""\
// Unimportant comment.
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 0
    assert len(info.markers) == 0


def test_02_functions():
    input_string = b"""\
#include <stdio.h>

/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
void hello_world(void) {
    print("hello world\\n");
}

/**
 * Some text.
 *
 * @relation(REQ-2, scope=function)
 */
void hello_world_2(void) {
    print("hello world\\n");
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 2
    assert info.markers[0].ng_source_line_begin == 6
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 10
    assert info.markers[0].reqs_objs[0].ng_source_line == 6
    assert info.markers[0].reqs_objs[0].ng_source_column == 14

    assert info.markers[1].ng_source_line_begin == 15
    assert info.markers[1].ng_range_line_begin == 12
    assert info.markers[1].ng_range_line_end == 19
    assert info.markers[1].reqs_objs[0].ng_source_line == 15
    assert info.markers[1].reqs_objs[0].ng_source_column == 14


def test_03_functions_multiline():
    input_string = b"""\
#include <stdio.h>

/**
 * Some text.
 *
 * @relation(
 *   REQ-1, scope=function
 * )
 */
void hello_world(void) {
    print("hello world\\n");
}

/**
 * Some text.
 *
 * @relation(REQ-2,
 * scope=function)
 */
void hello_world_2(void) {
    print("hello world\\n");
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 2
    assert info.markers[0].ng_source_line_begin == 6
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 12
    assert info.markers[0].reqs_objs[0].ng_source_line == 7
    assert info.markers[0].reqs_objs[0].ng_source_column == 6

    assert info.markers[1].ng_source_line_begin == 17
    assert info.markers[1].ng_range_line_begin == 14
    assert info.markers[1].ng_range_line_end == 22
    assert info.markers[1].reqs_objs[0].ng_source_line == 17
    assert info.markers[1].reqs_objs[0].ng_source_column == 14


def test_04_multiline_markers_with_underscores():
    """
    Bug: requirements UID not detected in source code when there's an EOL #2130
    https://github.com/strictdoc-project/strictdoc/issues/2130
    """

    input_string = b"""\
#include <stdio.h>

/**
 * @brief some text
 * @return some text.
 * @param[in] void
 * @param[out] void
 * @param[in, out] void
 * @pre
 * @post
 * @relation{INT_STP_016_0000, INT_STP_016_0001, INT_STP_016_0002,
 * scope=function}
 * @note Reference:
 */
stilib_result_t stilib_smu_start_state_check(void);
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 1
    assert info.markers[0].reqs == [
        "INT_STP_016_0000",
        "INT_STP_016_0001",
        "INT_STP_016_0002",
    ]

    assert info.markers[0].ng_source_line_begin == 11
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 15
    assert info.markers[0].reqs_objs[0].ng_source_line == 11
    assert info.markers[0].reqs_objs[0].ng_source_column == 14
    assert info.markers[0].reqs_objs[1].ng_source_line == 11
    assert info.markers[0].reqs_objs[1].ng_source_column == 32
    assert info.markers[0].reqs_objs[2].ng_source_line == 11
    assert info.markers[0].reqs_objs[2].ng_source_column == 50


def test_20_node_fields():
    input_string = b"""\
#include <stdio.h>

/**
 * Some text.
 *
 * INTENTION: This
 *            is
 *            the
 *            intention.
 *
 * @relation(REQ-1, scope=function)
 */
void hello_world(void) {
    print("hello world\\n");
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 1
    assert info.markers[0].ng_source_line_begin == 11
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 15
    assert info.markers[0].reqs_objs[0].ng_source_line == 11
    assert info.markers[0].reqs_objs[0].ng_source_column == 14
