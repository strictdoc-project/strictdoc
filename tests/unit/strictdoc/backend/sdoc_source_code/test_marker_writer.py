"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.marker_writer import MarkerWriter


def test_write_doxygen_comment():
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

    output_string = MarkerWriter().write(
        source_node,
        rewrites={},
        comment_file_bytes=bytes(input_string, encoding="utf8"),
    )
    assert output_string == bytes(input_string, encoding="utf8")


def test_write_node_fields():
    input_string = """\
/**
 * FOO: BAR
 */
"""

    source_node = MarkerParser.parse(
        input_string=input_string,
        line_start=1,
        line_end=16,
        comment_line_start=1,
        comment_byte_range=None,
        custom_tags={"FOO"},
    )

    expected_output_string = b"""\
/**
 * FOO: <MODIFIED>
 */
"""

    output_string = MarkerWriter().write(
        source_node,
        rewrites={"FOO": b"<MODIFIED>"},
        comment_file_bytes=bytes(input_string, encoding="utf8"),
    )
    assert output_string == expected_output_string
