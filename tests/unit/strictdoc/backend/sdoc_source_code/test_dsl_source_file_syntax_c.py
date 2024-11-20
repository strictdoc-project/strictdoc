import sys

import pytest

from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
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
    assert info.markers[0].ng_source_line_begin == 3
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 10
    assert info.markers[0].reqs_objs[0].ng_source_line == 6
    assert info.markers[0].reqs_objs[0].ng_source_column == 14

    assert info.markers[1].ng_source_line_begin == 12
    assert info.markers[1].ng_range_line_begin == 12
    assert info.markers[1].ng_range_line_end == 19
    assert info.markers[1].reqs_objs[0].ng_source_line == 15
    assert info.markers[1].reqs_objs[0].ng_source_column == 14
