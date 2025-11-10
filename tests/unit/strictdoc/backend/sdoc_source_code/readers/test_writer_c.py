"""
@relation(SDOC-SRS-146, scope=file)
"""

import sys

import pytest

from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)
from strictdoc.backend.sdoc_source_code.source_writer import SourceWriter

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Requires Python 3.9 or higher"
)


def test_02_c_functions():
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

    rewrites = {}
    for source_node_ in info.source_nodes:
        rewrites[source_node_] = b"<PATCHED>"

    source_writer = SourceWriter()
    output_string = source_writer.write(info, rewrites=rewrites)

    expected_output_string = b"""\
#include <stdio.h>

<PATCHED>
void hello_world(void) {
    print("hello world\\n");
}

<PATCHED>
void hello_world_2(void) {
    print("hello world\\n");
}
"""

    assert output_string == expected_output_string
