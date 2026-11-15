"""
@relation(SDOC-LLR-219, SDOC-LLR-223, scope=file)
"""

from typing import Dict, Optional

import pytest

from strictdoc.backend.sdoc_source_code.modelica_scanner import (
    ModelicaItem,
    ModelicaItemKind,
    ModelicaScanError,
    ModelicaScanResult,
    scan_modelica,
)

SOURCE = b"""\
within Rig.Sub;
encapsulated package P "a package // not a comment"
  import Modelica.Units.SI;
  /* a comment with end P; and model Fake */
  constant Real c = 1 "a constant";
  type Temp = Real(unit="K") "a short class";
  type Mode = enumeration(off "off", on "on") "an enumeration";
  type DTemp = der(Temp, 1);
  expandable connector Bus "a bus"
  end Bus;
  operator record Cpx "operator record"
    Real re, im "parts";
    encapsulated operator 'constructor'
      function fromReal "from real"
        input Real re;
        output Cpx c(re=re, im=0);
      algorithm
        while false loop
        end while;
      end fromReal;
    end 'constructor';
  end Cpx;
  partial model Base "base"
    parameter String s = "x";
    parameter String t = "x" "with description";
    parameter String u = if c > 0 then "a" else "b";
    replaceable model M = Base constrainedby Base "replaceable short";
    Real x[3] if c > 0 "conditional, with end; in the string";
    .Modelica.Blocks.Interfaces.RealInput y "leading dot" annotation(
      Placement(transformation(extent={{0,0},{1,1}})));
  protected
    Real z(start = 0, fixed = true) = x[end] annotation(Dialog(group="x"));
  initial equation
    z = 0;
  equation
    when initial() then
      reinit(z, 0);
    end when;
    for i in 1:3 loop
      x[i] = if i > 1 then 1 else 0;
    end for;
  end Base;
  model extends Base(s = "y") "extends form"
    Real w "w";
  end Base;
  function f "external"
    input Real a;
    output Real b;
  external "C" b = f(a) annotation(Library = "m");
  end f;
  annotation(Documentation(info = "<html>end P;</html>"));
end P;
"""


def _description(source: bytes, item: ModelicaItem) -> Optional[str]:
    if item.description_byte_range is None:
        return None
    begin, end = item.description_byte_range
    return source[begin:end].decode("utf-8")


def test_01_within_and_classes() -> None:
    result: ModelicaScanResult = scan_modelica(SOURCE)

    assert result.within == "Rig.Sub"
    classes = [
        item_.name
        for item_ in result.items
        if item_.kind is ModelicaItemKind.CLASS
    ]
    assert classes == [
        "Rig.Sub.P",
        "Rig.Sub.P.Temp",
        "Rig.Sub.P.Mode",
        "Rig.Sub.P.DTemp",
        "Rig.Sub.P.Bus",
        "Rig.Sub.P.Cpx",
        "Rig.Sub.P.Cpx.'constructor'",
        "Rig.Sub.P.Cpx.'constructor'.fromReal",
        "Rig.Sub.P.Base",
        "Rig.Sub.P.Base.M",
        "Rig.Sub.P.Base",
        "Rig.Sub.P.f",
    ]


def test_02_components_and_description_strings() -> None:
    result = scan_modelica(SOURCE)

    descriptions: Dict[str, Optional[str]] = {
        item_.name.removeprefix("Rig.Sub.P."): _description(SOURCE, item_)
        for item_ in result.items
        if item_.kind is ModelicaItemKind.COMPONENT
    }
    assert descriptions == {
        "c": '"a constant"',
        # Each declaration of a component list has its own description.
        "Cpx.re": None,
        "Cpx.im": '"parts"',
        "Cpx.'constructor'.fromReal.re": None,
        "Cpx.'constructor'.fromReal.c": None,
        # A string value is not a description string.
        "Base.s": None,
        "Base.t": '"with description"',
        "Base.u": None,
        "Base.x": '"conditional, with end; in the string"',
        "Base.y": '"leading dot"',
        "Base.z": None,
        "Base.w": '"w"',
        "f.a": None,
        "f.b": None,
    }


def test_03_class_lines_and_byte_ranges() -> None:
    result = scan_modelica(SOURCE)

    package = result.items[0]
    assert (package.line_begin, package.line_end) == (2, 52)
    assert _description(SOURCE, package) == '"a package // not a comment"'
    for item_ in result.items:
        text = SOURCE[item_.byte_begin : item_.byte_end]
        # A declaration in a component list ends at its comma.
        assert text.endswith(b";") or text.endswith(b","), item_.name
        assert SOURCE.count(b"\n", 0, item_.byte_begin) + 1 == (
            item_.line_begin
        ), item_.name
        assert SOURCE.count(b"\n", 0, item_.byte_end - 1) + 1 == (
            item_.line_end
        ), item_.name


def test_04_comments() -> None:
    source = b"""\
model Check "Checks @relation(TC-1, scope=class)"
  Real a "@relation(REQ-1, scope=component)";
equation
  // @relation(REQ-1, scope=range_start)
  a = 1;
  /* @relation(REQ-1, scope=range_end) */
end Check;
"""
    result = scan_modelica(source)

    assert [comment_.line_begin for comment_ in result.comments] == [4, 6]
    assert [
        source[comment_.byte_begin : comment_.byte_end]
        for comment_ in result.comments
    ] == [
        b"// @relation(REQ-1, scope=range_start)",
        b"/* @relation(REQ-1, scope=range_end) */",
    ]
    assert [item_.name for item_ in result.items] == ["Check", "Check.a"]


def test_05_crlf_and_utf8() -> None:
    source = SOURCE.replace(b"\n", b"\r\n").replace(
        b'"a constant"', '"a constant, 20 °C"'.encode()
    )
    expected = [
        (item_.name, item_.line_begin, item_.line_end)
        for item_ in scan_modelica(SOURCE).items
    ]

    result = scan_modelica(source)

    assert [
        (item_.name, item_.line_begin, item_.line_end) for item_ in result.items
    ] == expected
    constant = next(
        item_ for item_ in result.items if item_.name == "Rig.Sub.P.c"
    )
    assert _description(source, constant) == '"a constant, 20 °C"'


def test_06_empty_files() -> None:
    assert len(scan_modelica(b"").items) == 0
    assert len(scan_modelica(b"// only a comment\n").items) == 0


@pytest.mark.parametrize(
    "source,line",
    [
        (b'model A "unterminated\nend A;\n', 1),
        (b"model A\n  /* unterminated\nend A;\n", 2),
        (b"model A\n  Real x;\n", 2),
        (b"model A\n  Real x(;\nend A;\n", 3),
        (b"model A\n  Real x;\nend B;\n", 3),
        (b"x = 1;\n", 1),
    ],
    ids=[
        "unterminated string",
        "unterminated comment",
        "missing end",
        "unbalanced brackets",
        "end name mismatch",
        "not a class definition",
    ],
)
def test_07_errors_carry_the_line(source: bytes, line: int) -> None:
    with pytest.raises(ModelicaScanError) as exception_info:
        scan_modelica(source)
    assert exception_info.value.line == line
