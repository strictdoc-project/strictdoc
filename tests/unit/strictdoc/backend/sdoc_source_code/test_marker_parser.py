"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

import pytest

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker


def test_01_basic_nominal():
    input_strings = [
        "@relation(REQ-1, scope=function)\n",
        "@relation(REQ_1, scope=function)\n",
        "@relation(REQ.1, scope=function)\n",
        "@relation(REQ/1, scope=function)\n",
    ]

    for input_string_ in input_strings:
        source_node = MarkerParser.parse(
            input_string=input_string_,
            line_start=1,
            line_end=1,
            comment_line_start=1,
            comment_byte_range=None,
        )
        function_range = source_node.markers[0]
        assert isinstance(function_range, LanguageItemMarker)
        assert function_range.ng_source_line_begin == 1
        assert function_range.ng_range_line_begin == 1
        assert function_range.ng_range_line_end == 1
        assert function_range.reqs_objs[0].ng_source_line == 1
        assert function_range.reqs_objs[0].ng_source_column == 11


def test_10_parses_with_leading_newlines():
    input_string = """\


@relation(REQ-1, scope=function)
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=5,
        comment_line_start=1,
        comment_byte_range=None,
    )
    function_range = source_node.markers[0]

    assert isinstance(function_range, LanguageItemMarker)
    assert function_range.ng_source_line_begin == 3
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 3
    assert function_range.reqs_objs[0].ng_source_column == 11


def test_11_parses_with_leading_whitespace():
    input_string = """\


    @relation(REQ-1, scope=function)
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=3,
        comment_line_start=1,
        comment_byte_range=None,
    )
    function_range = source_node.markers[0]

    assert isinstance(function_range, LanguageItemMarker)
    assert function_range.ng_source_line_begin == 3
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 3
    assert function_range.reqs_objs[0].ng_source_line == 3
    assert function_range.reqs_objs[0].ng_source_column == 15


def test_20_parses_within_doxygen_comment():
    input_string = """\
/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=5,
        comment_line_start=1,
        comment_byte_range=None,
    )
    function_range = source_node.markers[0]

    assert isinstance(function_range, LanguageItemMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14


def test_21_parses_within_doxygen_comment_two_markers():
    input_string = """\
/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 * @relation(REQ-2, scope=function)
 */
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=6,
        comment_line_start=1,
        comment_byte_range=None,
    )
    function_range = source_node.markers[0]

    assert isinstance(function_range, LanguageItemMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 6
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14


def test_22_parses_within_doxygen_comment_curly_braces():
    input_string = """\
/**
 * Some text.
 *
 * @relation{REQ-1, scope=function}
 */
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=5,
        comment_line_start=1,
        comment_byte_range=None,
    )
    function_range = source_node.markers[0]

    assert isinstance(function_range, LanguageItemMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 5
    assert function_range.reqs_objs[0].ng_source_line == 4
    assert function_range.reqs_objs[0].ng_source_column == 14


def test_23_parses_within_doxygen_comment():
    input_string = """\
/**
 * Some text.
 *
 * @relation(
 *     REQ-1,
 *     REQ-2,
 *     REQ-3,
 *     scope=function
 * )
 * @relation(
 *     REQ-4,
 *     REQ-5,
 *     REQ-6,
 *     scope=function
 * )
 */
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=16,
        comment_line_start=1,
        comment_byte_range=None,
    )

    function_range = source_node.markers[0]
    assert isinstance(function_range, LanguageItemMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 16
    assert function_range.reqs_objs[0].uid == "REQ-1"
    assert function_range.reqs_objs[0].ng_source_line == 5
    assert function_range.reqs_objs[0].ng_source_column == 8
    assert function_range.reqs_objs[1].uid == "REQ-2"
    assert function_range.reqs_objs[1].ng_source_line == 6
    assert function_range.reqs_objs[1].ng_source_column == 8
    assert function_range.reqs_objs[2].uid == "REQ-3"
    assert function_range.reqs_objs[2].ng_source_line == 7
    assert function_range.reqs_objs[2].ng_source_column == 8

    function_range = source_node.markers[1]
    assert isinstance(function_range, LanguageItemMarker)
    assert function_range.ng_source_line_begin == 10
    assert function_range.ng_range_line_begin == 1
    assert function_range.ng_range_line_end == 16
    assert function_range.reqs_objs[0].uid == "REQ-4"
    assert function_range.reqs_objs[0].ng_source_line == 11
    assert function_range.reqs_objs[0].ng_source_column == 8
    assert function_range.reqs_objs[1].uid == "REQ-5"
    assert function_range.reqs_objs[1].ng_source_line == 12
    assert function_range.reqs_objs[1].ng_source_column == 8
    assert function_range.reqs_objs[2].uid == "REQ-6"
    assert function_range.reqs_objs[2].ng_source_line == 13
    assert function_range.reqs_objs[2].ng_source_column == 8


def test_24_parses_multiline_marker():
    input_string = """\
/**
 * Some text.
 *
 * @relation(
 *     REQ-1,
 *     REQ-2,
 *     REQ-3,
 *     scope=line
 * )
 * HERE SOME LINE
 */
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=11,
        comment_line_start=1,
        comment_byte_range=None,
    )

    function_range = source_node.markers[0]
    assert isinstance(function_range, LineMarker)
    assert function_range.ng_source_line_begin == 4
    assert function_range.ng_range_line_begin == 4
    assert function_range.ng_range_line_end == 10
    assert function_range.reqs_objs[0].uid == "REQ-1"
    assert function_range.reqs_objs[0].ng_source_line == 5
    assert function_range.reqs_objs[0].ng_source_column == 8
    assert function_range.reqs_objs[1].uid == "REQ-2"
    assert function_range.reqs_objs[1].ng_source_line == 6
    assert function_range.reqs_objs[1].ng_source_column == 8
    assert function_range.reqs_objs[2].uid == "REQ-3"
    assert function_range.reqs_objs[2].ng_source_line == 7
    assert function_range.reqs_objs[2].ng_source_column == 8


def test_30_parser_dedents_field_lines():
    """
    Since source code fields will likely opt for text rendering (instead of RST),
    ensure that ASCII formating is preserved reasonably.
    """
    input_string = """\
    /**
     * FIELD1: Nothing to dedent here.
     *
     * FIELD2: Nothing to
     * dedent here.
     *
     * FIELD3: Dedent
     *         - this list
     *           - but keep
     *             - inner indent
     *
     * FIELD4:
     *        ASCII art
     *    ___           ___
     *  ( foo ) <---> ( bar )
     *    ‾‾‾           ‾‾‾
     */"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=7,
        comment_line_start=1,
        comment_byte_range=None,
        custom_tags=["FIELD1", "FIELD2", "FIELD3", "FIELD4"],
    )
    assert source_node.fields["FIELD1"] == "Nothing to dedent here."
    assert source_node.fields["FIELD2"] == "Nothing to\ndedent here."
    assert source_node.fields["FIELD3"] == (
        "Dedent\n- this list\n  - but keep\n    - inner indent"
    )
    assert source_node.fields["FIELD4"] == (
        "\n"
        "      ASCII art\n"
        "  ___           ___\n"
        "( foo ) <---> ( bar )\n"
        "  ‾‾‾           ‾‾‾"
    )


@pytest.mark.parametrize(
    "input_string,default_scope,expected_type",
    [
        ("@relation(REQ-1)\n", "function", LanguageItemMarker),
        ("@relation(REQ-1, scope=line)\n", None, LineMarker),
        ("@relation(REQ-1, scope=line)\n", "function", LineMarker),
    ],
    ids=[
        "default, no user value",
        "no default, user value",
        "override default with user value",
    ],
)
def test_40_default_scope(input_string, default_scope, expected_type):
    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=1,
        comment_line_start=1,
        comment_byte_range=None,
        default_scope=default_scope,
    )
    assert isinstance(source_node.markers[0], expected_type)


def test_41_omitted_scope_with_role():
    input_string = "@relation(REQ-1, role=implementation)\n"
    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=1,
        comment_line_start=1,
        comment_byte_range=None,
        default_scope="function",
    )
    assert isinstance(source_node.markers[0], LanguageItemMarker)
    assert source_node.markers[0].role == "implementation"


def test_42_error_on_missing_scope():
    input_string = "some comment\n@relation(REQ-1)\n"

    excinfo: pytest.ExceptionInfo
    with pytest.raises(StrictDocSemanticError) as excinfo:
        MarkerParser.parse(
            input_string=input_string,
            line_start=1,
            line_end=1,
            comment_line_start=10,
            comment_byte_range=None,
            filename="main.py",
        )
    assert (
        excinfo.value.title
        == "@relation marker for requirements REQ-1 misses scope argument."
    )
    assert (
        excinfo.value.hint
        == "Scope can only be omitted if supported by language, as e.g. with Rust doc comments."
    )
    assert (
        excinfo.value.example
        == "Add a scope argument. Example:\n@relation(REQ-1, scope=function)"
    )
    assert excinfo.value.file_path == "main.py"
    assert excinfo.value.line == 11


def test_80_linux_spdx_example():
    input_string = """\
/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 *
 * SPDX-Req-ID: SRC-1
 *
 * SPDX-Req-HKey: TBD
 *
 * SPDX-Text: This
 *            is
 *            a statement
 *
 *            And this is the same statement's another paragraph.
 */
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=11,
        comment_line_start=1,
        comment_byte_range=None,
        custom_tags={"SPDX-Req-ID", "SPDX-Req-HKey", "SPDX-Text"},
    )

    assert list(source_node.fields.keys()) == [
        "SPDX-Req-ID",
        "SPDX-Req-HKey",
        "SPDX-Text",
    ]

    assert (
        source_node.fields["SPDX-Text"]
        == """\
This
is
a statement

And this is the same statement's another paragraph.\
"""
    )
