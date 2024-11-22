import sys

import pytest

from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Requires Python 3.9 or higher"
)


def test_01_class_function_declaration():
    input_string = b"""\
class Foo
{
  public:
    /**
     * @relation(REQ-1, scope=function)
     */
    bool CanSend(const CanFrame &frame);
};
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 1
    assert len(info.markers) == 1

    function: Function = info.functions[0]
    assert function.name == "Foo::CanSend"
    assert function.line_begin == 4
    assert function.line_end == 7

    marker: FunctionRangeMarker = info.markers[0]
    assert marker.ng_range_line_begin == 4
    assert marker.ng_range_line_end == 7


def test_02_nested_class_function_declaration():
    input_string = b"""\
class Foo {
class Bar {
  public:
    /**
     * @relation(REQ-1, scope=function)
     */
    bool CanSend(const CanFrame &frame);
};
};
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 1
    assert len(info.markers) == 1

    function: Function = info.functions[0]
    assert function.name == "Foo::Bar::CanSend"
    assert function.line_begin == 4
    assert function.line_end == 7

    marker: FunctionRangeMarker = info.markers[0]
    assert marker.ng_range_line_begin == 4
    assert marker.ng_range_line_end == 7


def test_11_class_function_definition():
    input_string = b"""\
/**
 * @relation(REQ-1, scope=function)
 */
bool Foo::Bar::CanSend(const CanFrame &frame) {
    return true;
}
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 1
    assert len(info.markers) == 1

    function: Function = info.functions[0]
    assert function.name == "Foo::Bar::CanSend"
    assert function.line_begin == 1
    assert function.line_end == 6

    marker: FunctionRangeMarker = info.markers[0]
    assert marker.ng_range_line_begin == 1
    assert marker.ng_range_line_end == 6


def test_12_class_function_declaration_returning_reference():
    input_string = b"""\
class TrkVertex
{
   public:
    double x_ = 0;  //!< mm, x axis pointing right
    double y_ = 0;  //!< mm, y axis pointing up

    /**
     * @relation(REQ-1, scope=function)
     */
    TrkVertex& operator-=(const TrkVertex& c);
};
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 1
    assert len(info.markers) == 1

    function: Function = info.functions[0]
    assert function.name == "TrkVertex::operator-="
    assert function.line_begin == 7
    assert function.line_end == 10

    marker: FunctionRangeMarker = info.markers[0]
    assert marker.ng_range_line_begin == 7
    assert marker.ng_range_line_end == 10


def test_20_constructor_and_destructor_declarations():
    input_string = b"""\
class TrkVertex
{
   public:
   /**
     * @relation(REQ-1, scope=function)
     */
    TrkVertex();

    /**
     * @relation(REQ-1, scope=function)
     */
    TrkVertex(double x, double y);

    /**
     * @relation(REQ-1, scope=function)
     */
    ~TrkVertex();
};
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 3
    assert len(info.markers) == 3

    function_1: Function = info.functions[0]
    assert function_1.name == "TrkVertex::TrkVertex"
    assert function_1.line_begin == 4
    assert function_1.line_end == 7

    function_2: Function = info.functions[1]
    assert function_2.name == "TrkVertex::TrkVertex"
    assert function_2.line_begin == 9
    assert function_2.line_end == 12

    function_3: Function = info.functions[2]
    assert function_3.name == "TrkVertex::~TrkVertex"
    assert function_3.line_begin == 14
    assert function_3.line_end == 17

    marker_1: FunctionRangeMarker = info.markers[0]
    assert marker_1.ng_range_line_begin == 4
    assert marker_1.ng_range_line_end == 7

    marker_2: FunctionRangeMarker = info.markers[1]
    assert marker_2.ng_range_line_begin == 9
    assert marker_2.ng_range_line_end == 12

    marker_3: FunctionRangeMarker = info.markers[2]
    assert marker_3.ng_range_line_begin == 14
    assert marker_3.ng_range_line_end == 17


def test_21_constructor_and_destructor_definitions():
    input_string = b"""\
class TrkVertex
{
   public:
   /**
     * @relation(REQ-1, scope=function)
     */
    TrkVertex() {}

    /**
     * @relation(REQ-1, scope=function)
     */
    TrkVertex(double x, double y) {}

    /**
     * @relation(REQ-1, scope=function)
     */
    ~TrkVertex() {}
};
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 3
    assert len(info.markers) == 3

    function_1: Function = info.functions[0]
    assert function_1.name == "TrkVertex::TrkVertex"
    assert function_1.line_begin == 4
    assert function_1.line_end == 7

    function_2: Function = info.functions[1]
    assert function_2.name == "TrkVertex::TrkVertex"
    assert function_2.line_begin == 9
    assert function_2.line_end == 12

    function_3: Function = info.functions[2]
    assert function_3.name == "TrkVertex::~TrkVertex"
    assert function_3.line_begin == 14
    assert function_3.line_end == 17

    marker_1: FunctionRangeMarker = info.markers[0]
    assert marker_1.ng_range_line_begin == 4
    assert marker_1.ng_range_line_end == 7

    marker_2: FunctionRangeMarker = info.markers[1]
    assert marker_2.ng_range_line_begin == 9
    assert marker_2.ng_range_line_end == 12

    marker_3: FunctionRangeMarker = info.markers[2]
    assert marker_3.ng_range_line_begin == 14
    assert marker_3.ng_range_line_end == 17
