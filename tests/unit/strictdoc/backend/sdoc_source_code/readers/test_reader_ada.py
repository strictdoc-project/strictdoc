"""
@relation(SDOC-SRS-208, scope=file)
"""

from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_ada import (
    SourceFileTraceabilityReader_Ada,
)


def test_00_empty_file():
    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(b"", file_path="NOT_RELEVANT")

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 0
    assert len(info.markers) == 0


def test_01_subprogram_bodies():
    input_string = b"""\
with Ada.Text_IO;

package body Hello is
   -- Some text.
   --
   -- @relation(REQ-1, scope=function)
   procedure Hello_World is
   begin
      Ada.Text_IO.Put_Line ("hello world");
   end Hello_World;

   -- @relation(REQ-2, scope=function)
   function Answer return Integer is (42);
end Hello;
"""

    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(input_string, file_path="hello.adb")

    assert [function_.display_name for function_ in info.functions] == [
        "Hello.Hello_World",
        "Hello.Answer",
    ]
    assert len(info.markers) == 2
    assert info.markers[0].ng_source_line_begin == 6
    assert info.markers[0].ng_range_line_begin == 4
    assert info.markers[0].ng_range_line_end == 10
    assert info.markers[0].reqs_objs[0].ng_source_column == 17
    assert info.markers[1].ng_range_line_begin == 12
    assert info.markers[1].ng_range_line_end == 13
    assert info.functions[0].attributes == {FunctionAttribute.DEFINITION}


def test_02_package_spec_declarations():
    input_string = b"""\
package Hello.Child is
   -- @relation(REQ-1, scope=function)
   procedure Hello_World (Count : Integer);

   package Inner is
      -- @relation(REQ-2, scope=function)
      function Answer return Integer;
   end Inner;
end Hello.Child;
"""

    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(input_string, file_path="hello-child.ads")

    assert [function_.display_name for function_ in info.functions] == [
        "Hello.Child.Hello_World",
        "Hello.Child.Inner.Answer",
    ]
    assert info.functions[0].attributes == {FunctionAttribute.DECLARATION}
    assert info.markers[0].ng_range_line_begin == 2
    assert info.markers[0].ng_range_line_end == 3
    assert info.markers[1].ng_range_line_begin == 6
    assert info.markers[1].ng_range_line_end == 7


def test_03_nested_subprogram():
    input_string = b"""\
package body Hello is
   procedure Outer is
      -- @relation(REQ-1, scope=function)
      procedure Inner is null;
   begin
      Inner;
   end Outer;
end Hello;
"""

    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(input_string, file_path="hello.adb")

    assert [function_.display_name for function_ in info.functions] == [
        "Hello.Outer",
        "Hello.Outer.Inner",
    ]
    assert info.functions[1].markers[0].reqs == ["REQ-1"]


def test_04_file_and_range_markers():
    input_string = b"""\
-- @relation(REQ-1, scope=file)

package body Hello is
   -- @relation(REQ-2, scope=range_start)
   Count : Integer := 0;
   -- @relation(REQ-2, scope=range_end)
   Label : String := "-- @relation(REQ-3, scope=line)";
end Hello;
"""

    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(input_string, file_path="hello.adb")

    assert len(info.functions) == 0
    assert info.markers[0].reqs == ["REQ-1"]
    assert info.markers[0].ng_range_line_begin == 1
    assert info.markers[0].ng_range_line_end == 8
    assert info.markers[1].reqs == ["REQ-2"]
    assert info.markers[1].ng_range_line_begin == 4
    assert info.markers[1].ng_range_line_end == 6
    assert "REQ-3" not in info.ng_map_reqs_to_markers


def test_05_warning_for_scope_function_marker_without_subprogram(capsys):
    input_string = b"""\
package Hello is
   -- @relation(REQ-1, scope=function)

   procedure Hello_World;
end Hello;
"""

    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(input_string, file_path="hello.ads")

    assert len(info.functions[0].markers) == 0
    assert (
        "hello.ads:2: skipping a scope=function marker for REQ-1"
        in capsys.readouterr().out
    )


def test_06_lower_case_name_and_overloads():
    input_string = b"""\
package body Hello is
   procedure DO_IT is null;

   procedure Put (Value : Integer) is null;

   procedure Put (Value : Float) is null;
end Hello;
"""

    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(input_string, file_path="hello.adb")

    assert info.functions[0].name == "hello.do_it"
    assert info.functions[0].display_name == "Hello.DO_IT"
    assert info.functions[1].name == info.functions[2].name == "hello.put"


def test_07_marked_overloads_keep_all_markers():
    input_string = b"""\
package body Hello is
   -- @relation(REQ-1, scope=function)
   procedure Put (Value : Integer) is null;

   -- @relation(REQ-2, scope=function)
   procedure Put (Value : Float) is null;
end Hello;
"""

    reader = SourceFileTraceabilityReader_Ada()

    info = reader.read(input_string, file_path="hello.adb")

    assert [marker_.reqs for marker_ in info.markers] == [["REQ-1"], ["REQ-2"]]
    assert info.functions[0].markers[0].reqs == ["REQ-1"]
    assert info.functions[1].markers[0].reqs == ["REQ-2"]
