"""
@relation(SDOC-SRS-208, scope=file)
"""

import pytest

from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
    RangeMarkerType,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import RangeMarker
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_modelica import (
    SourceFileTraceabilityReader_Modelica,
)

SOURCE = b"""\
within Rig;
model Check "Checks of TC-1 @relation(TC-1, scope=class)"
  parameter Real k = 1 "Gain";
  Real a, b "Rise check @relation(REQ-2, REQ-3)";
equation
  a = k;
  b = a;
end Check;
"""


def test_00_empty_file() -> None:
    info = SourceFileTraceabilityReader_Modelica().read(b"")

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 0
    assert len(info.markers) == 0


def test_01_classes_and_components() -> None:
    """
    @relation(SDOC-LLR-219, scope=function)
    """

    info = SourceFileTraceabilityReader_Modelica().read(SOURCE)

    assert [
        (function_.name, function_.line_begin, function_.line_end)
        for function_ in info.functions
    ] == [
        ("Rig.Check", 2, 8),
        ("Rig.Check.k", 3, 3),
        ("Rig.Check.a", 4, 4),
        ("Rig.Check.b", 4, 4),
    ]
    for function_ in info.functions:
        assert function_.display_name == function_.name


def test_02_markers_in_description_strings() -> None:
    """
    @relation(SDOC-LLR-220, scope=function)
    """

    info = SourceFileTraceabilityReader_Modelica().read(SOURCE)

    assert len(info.markers) == 2
    class_marker, component_marker = info.markers
    assert isinstance(class_marker, LanguageItemMarker)
    assert class_marker.scope is RangeMarkerType.CLASS
    assert class_marker.reqs == ["TC-1"]
    assert class_marker.ng_range_line_begin == 2
    assert class_marker.ng_range_line_end == 8
    assert class_marker.ng_source_line_begin == 2
    assert class_marker.get_description() == "class Rig.Check"

    # The scope of a marker in a description string can be omitted.
    assert isinstance(component_marker, LanguageItemMarker)
    assert component_marker.scope is RangeMarkerType.COMPONENT
    assert component_marker.reqs == ["REQ-2", "REQ-3"]
    assert component_marker.ng_range_line_begin == 4
    assert component_marker.ng_range_line_end == 4
    assert component_marker.get_description() == "component Rig.Check.b"
    assert info.ng_map_names_to_markers["Rig.Check.b"] == [component_marker]
    assert len(info.ng_map_names_to_markers["Rig.Check.a"]) == 0


def test_03_marker_in_a_multiline_description_string() -> None:
    """
    @relation(SDOC-LLR-220, scope=function)
    """

    source = b"""\
model Check
  "Checks of TC-1:
   one line of text,
   @relation(TC-1, scope=class)"
end Check;
"""
    info = SourceFileTraceabilityReader_Modelica().read(source)

    assert len(info.markers) == 1
    marker = info.markers[0]
    assert isinstance(marker, LanguageItemMarker)
    assert marker.ng_source_line_begin == 4
    assert marker.ng_range_line_begin == 1
    assert marker.ng_range_line_end == 5


def test_04_wrong_scope_in_a_description_string(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    @relation(SDOC-LLR-220, scope=function)
    """

    source = b"""\
model Check "@relation(TC-1, scope=component)"
  Real a "@relation(REQ-1, scope=class) @relation(REQ-2, scope=line)";
end Check;
"""
    info = SourceFileTraceabilityReader_Modelica().read(
        source, file_path="Check.mo"
    )

    assert len(info.markers) == 0
    output = capsys.readouterr().out
    assert (
        "warning: Modelica source reader: Check.mo:1: skipping a "
        "scope=component marker in the description string of the class "
        "Check: only scope=class is valid there."
    ) in output
    assert (
        "Check.mo:2: skipping a scope=class marker in the description "
        "string of the component Check.a: only scope=component is valid "
        "there."
    ) in output
    assert "Check.mo:2: skipping a scope=line marker" in output


def test_05_file_line_and_range_markers_in_comments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    @relation(SDOC-LLR-221, scope=function)
    """

    source = b"""\
// @relation(REQ-1, scope=file)
model Check
  Real a;
equation
  /* @relation(REQ-2, scope=range_start) */
  a = 1;
  // @relation(REQ-2, scope=range_end)
  // @relation(REQ-3, scope=line)
  a = 1;
  // @relation(REQ-4, scope=class)
end Check;
"""
    info = SourceFileTraceabilityReader_Modelica().read(
        source, file_path="Check.mo"
    )

    file_marker = info.markers[0]
    assert isinstance(file_marker, LanguageItemMarker)
    assert file_marker.scope is RangeMarkerType.FILE
    assert file_marker.ng_range_line_begin == 1
    assert file_marker.ng_range_line_end == 11

    range_markers = [
        marker_ for marker_ in info.markers if isinstance(marker_, RangeMarker)
    ]
    assert [
        (marker_.ng_range_line_begin, marker_.ng_range_line_end)
        for marker_ in range_markers
    ] == [(5, 7), (5, 7)]

    line_markers = [
        marker_ for marker_ in info.markers if isinstance(marker_, LineMarker)
    ]
    assert [marker_.ng_range_line_begin for marker_ in line_markers] == [8]

    assert "REQ-4" not in [
        uid_ for marker_ in info.markers for uid_ in marker_.reqs
    ]
    assert (
        "warning: Modelica source reader: Check.mo:10: skipping a "
        "scope=class marker in a comment."
    ) in capsys.readouterr().out


def test_06_file_that_the_scanner_cannot_read(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    @relation(SDOC-LLR-223, scope=function)
    """

    source = b"""\
model Check
  // @relation(REQ-1, scope=range_start)
  Real a(;
  // @relation(REQ-1, scope=range_end)
end Check;
"""
    info = SourceFileTraceabilityReader_Modelica().read(
        source, file_path="Check.mo"
    )

    assert len(info.functions) == 0
    assert [
        (marker_.ng_range_line_begin, marker_.ng_range_line_end)
        for marker_ in info.markers
        if isinstance(marker_, RangeMarker)
    ] == [(2, 4), (2, 4)]
    assert (
        "warning: Modelica source reader: Check.mo:5: ',' or ';' expected "
        "before the end of the file. Reading the file, line and range "
        "markers of the file without classes and components."
    ) in capsys.readouterr().out


def test_07_byte_ranges_with_bom_and_utf8() -> None:
    source = (
        b"\xef\xbb\xbf"
        + 'model Check "20 °C @relation(TC-1, scope=class)"\n'.encode()
        + b"end Check;\n"
    )

    info = SourceFileTraceabilityReader_Modelica().read(source)

    check_class = info.functions[0]
    assert check_class.code_byte_range is not None
    assert (
        source[
            check_class.code_byte_range.start : check_class.code_byte_range.end
        ]
        .decode("utf-8")
        .startswith("model Check")
    )
    assert source.endswith(b"end Check;\n")
    assert len(info.markers) == 1
