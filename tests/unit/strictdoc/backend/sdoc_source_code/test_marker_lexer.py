"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

from strictdoc.backend.sdoc_source_code.comment_parser.marker_lexer import (
    MarkerLexer,
)


def test_01_basic_nominal():
    tree = MarkerLexer.parse("")
    assert len(tree.children) == 0
    assert tree.data == "start"


def test_02_single_marker():
    input_strings = [
        "@relation(REQ-1, REQ-2, scope=function)",
        "@relation(REQ_1, REQ_2, scope=function)",
        "@relation(REQ.1, REQ.2, scope=function)",
        "@relation(REQ/1, REQ/2, scope=function)",
    ]
    for input_string_ in input_strings:
        tree = MarkerLexer.parse(input_string_)
        assert len(tree.children) == 1
        assert tree.data == "start"
        assert tree.children[0].data == "relation_marker"
        assert tree.children[0].children[0].data == "relation_node_uid"
        assert tree.children[0].children[0].children[0].value.startswith("REQ")
        assert tree.children[0].children[1].data == "relation_node_uid"
        assert tree.children[0].children[1].children[0].value.startswith("REQ")
        assert tree.children[0].children[2].data == "relation_scope"
        assert tree.children[0].children[2].children[0].value == "function"


def test_03_single_marker_with_role():
    tree = MarkerLexer.parse(
        "@relation(REQ-1, scope=function, role=Implementation)"
    )
    assert len(tree.children) == 1
    assert tree.data == "start"
    assert tree.children[0].data == "relation_marker"
    assert tree.children[0].children[0].data == "relation_node_uid"
    assert tree.children[0].children[0].children[0].value == "REQ-1"
    assert tree.children[0].children[1].data == "relation_scope"
    assert tree.children[0].children[1].children[0].value == "function"
    assert tree.children[0].children[2].data == "relation_role"
    assert tree.children[0].children[2].children[0].value == "Implementation"


def test_10_single_marker_with_newline():
    input_string = "@relation(REQ-1, scope=function)\n"

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    assert len(tree.children) == 1
    assert tree.children[0].data == "relation_marker"
    assert tree.children[0].children[0].data == "relation_node_uid"
    assert tree.children[0].children[0].children[0].value.startswith("REQ")
    assert tree.children[0].children[1].data == "relation_scope"
    assert tree.children[0].children[1].children[0].value == "function"


def test_11_single_marker_with_newline():
    input_string = """\
@relation(
    REQ-1,
    scope=function
)
"""

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    assert len(tree.children) == 1
    assert tree.children[0].data == "relation_marker"
    assert tree.children[0].children[0].data == "relation_node_uid"
    assert tree.children[0].children[0].children[0].value.startswith("REQ")
    assert tree.children[0].children[1].data == "relation_scope"
    assert tree.children[0].children[1].children[0].value == "function"


def test_12_python_preprocessed_input():
    input_string = """\
  @relation(REQ-001, REQ-002, REQ-003, scope=range_start)
"""

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    assert len(tree.children) == 1
    assert tree.children[0].data == "relation_marker"
    assert tree.children[0].children[0].data == "relation_node_uid"
    assert tree.children[0].children[0].children[0].value.startswith("REQ")
    assert tree.children[0].children[1].data == "relation_node_uid"
    assert tree.children[0].children[1].children[0].value.startswith("REQ")
    assert tree.children[0].children[2].data == "relation_node_uid"
    assert tree.children[0].children[2].children[0].value.startswith("REQ")
    assert tree.children[0].children[3].data == "relation_scope"
    assert tree.children[0].children[3].children[0].value == "range_start"


def test_13_python_preprocessed_input():
    input_string = """\
  @relation(REQ-001, REQ-002, REQ-003, scope=range_start)
  print("Hello world")
  @relation(REQ-001, REQ-002, REQ-003, scope=range_end)
""".lstrip()

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    assert len(tree.children) == 2
    assert tree.children[0].data == "relation_marker"
    assert tree.children[0].children[0].data == "relation_node_uid"
    assert tree.children[0].children[0].children[0].value.startswith("REQ")
    assert tree.children[0].children[1].data == "relation_node_uid"
    assert tree.children[0].children[1].children[0].value.startswith("REQ")
    assert tree.children[0].children[2].data == "relation_node_uid"
    assert tree.children[0].children[2].children[0].value.startswith("REQ")
    assert tree.children[0].children[3].data == "relation_scope"
    assert tree.children[0].children[3].children[0].value == "range_start"

    assert tree.children[1].data == "relation_marker"
    assert tree.children[1].children[0].data == "relation_node_uid"
    assert tree.children[1].children[0].children[0].value.startswith("REQ")
    assert tree.children[1].children[1].data == "relation_node_uid"
    assert tree.children[1].children[1].children[0].value.startswith("REQ")
    assert tree.children[1].children[2].data == "relation_node_uid"
    assert tree.children[1].children[2].children[0].value.startswith("REQ")
    assert tree.children[1].children[3].data == "relation_scope"
    assert tree.children[1].children[3].children[0].value == "range_end"


def test_20_single_marker_and_normal_line():
    input_string = """\
FOOBAR

@relation(
    REQ-1,
    scope=function
)

FOOBAR
"""

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    assert len(tree.children) == 1
    assert tree.children[0].data == "relation_marker"
    assert tree.children[0].children[0].data == "relation_node_uid"
    assert tree.children[0].children[0].children[0].value.startswith("REQ")
    assert tree.children[0].children[1].data == "relation_scope"
    assert tree.children[0].children[1].children[0].value == "function"


def test_30_relation_and_field():
    input_string = """\
FOOBAR

@relation(
    REQ-1,
    scope=function
)

STATEMENT: When C,
           The system A shall do B

STATEMENT: When Z,
           The system X shall do Y

STATEMENT: When 1, The system 2 shall do 3

STATEMENT: When 1, The system 2 shall do 3

FOOBAR
"""

    tree = MarkerLexer.parse(input_string, parse_nodes=True)
    assert tree.data == "start"

    assert len(tree.children) == 5
    assert tree.children[0].data == "relation_marker"
    assert tree.children[0].children[0].data == "relation_node_uid"
    assert tree.children[0].children[0].children[0].value.startswith("REQ")
    assert tree.children[0].children[1].data == "relation_scope"
    assert tree.children[0].children[1].children[0].value == "function"

    assert tree.children[1].data == "node_field"
    assert tree.children[1].children[0].data == "node_name"
    assert tree.children[1].children[0].children[0].value == "STATEMENT"
    assert tree.children[1].children[1].data == "node_multiline_value"
    assert len(tree.children[1].children[1].children) == 2
    assert tree.children[1].children[1].children[0].value == "When C,"
    assert (
        tree.children[1].children[1].children[1].value
        == "           The system A shall do B"
    )

    assert tree.children[2].data == "node_field"
    assert tree.children[2].children[0].data == "node_name"
    assert tree.children[2].children[0].children[0].value == "STATEMENT"
    assert tree.children[2].children[1].data == "node_multiline_value"
    assert len(tree.children[2].children[1].children) == 2
    assert tree.children[2].children[1].children[0].value == "When Z,"
    assert (
        tree.children[2].children[1].children[1].value
        == "           The system X shall do Y"
    )

    assert tree.children[3].data == "node_field"
    assert tree.children[3].children[0].data == "node_name"
    assert tree.children[3].children[0].children[0].value == "STATEMENT"
    assert tree.children[3].children[1].data == "node_multiline_value"
    assert len(tree.children[3].children[1].children) == 1
    assert (
        tree.children[3].children[1].children[0].value
        == "When 1, The system 2 shall do 3"
    )

    assert tree.children[4].data == "node_field"
    assert tree.children[4].children[0].data == "node_name"
    assert tree.children[4].children[0].children[0].value == "STATEMENT"
    assert tree.children[4].children[1].data == "node_multiline_value"
    assert len(tree.children[4].children[1].children) == 1
    assert (
        tree.children[4].children[1].children[0].value
        == "When 1, The system 2 shall do 3"
    )


def test_31_single_node_field():
    """
    Ensure that a single field can be parsed.

    It turns out that this particular case is pretty sensitive with respect to
    how the grammar is constructed.
    """

    input_string = """
        STATEMENT: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(input_string, parse_nodes=True)
    assert tree.data == "start"

    assert len(tree.children) == 1
    assert tree.children[0].data == "node_field"
    assert tree.children[0].children[0].data == "node_name"
    assert tree.children[0].children[0].children[0].value == "STATEMENT"
    assert tree.children[0].children[1].data == "node_multiline_value"
    assert (
        tree.children[0].children[1].children[0].value
        == "This can likely replace _weak below with no problem."
    )


def test_31B_single_node_field():
    """
    Ensure that a single field can be parsed.

    It turns out that this particular case is pretty sensitive with respect to
    how the grammar is constructed.

    NOTE: The input below contains random whitespace.
    """

    input_string = """\
#include <stdio.h>

   
   Some text.
  
   INTENTION: Intention A.
  
  
    """  # noqa: W293

    tree = MarkerLexer.parse(input_string, parse_nodes=True)
    assert tree.data == "start"

    assert len(tree.children) == 1
    assert tree.children[0].data == "node_field"
    assert tree.children[0].children[0].data == "node_name"
    assert tree.children[0].children[0].children[0].value == "INTENTION"
    assert tree.children[0].children[1].data == "node_multiline_value"
    assert tree.children[0].children[1].children[0].value == "Intention A."


def test_31C_single_node_field():
    """
    Ensure that a single field can be parsed.

    It turns out that this particular case is pretty sensitive with respect to
    how the grammar is constructed.

    NOTE: The input below contains random whitespace.
    """

    input_string = """\
#include <stdio.h>
   
    Some text.
  
   INTENTION: Intention A.
   
   @relation(REQ-1, scope=function)
   
void hello_world(void) {
    print("hello world\\n");
}
"""  # noqa: W293

    tree = MarkerLexer.parse(input_string, parse_nodes=True)
    assert tree.data == "start"

    assert len(tree.children) == 2
    assert tree.children[0].data == "node_field"
    assert tree.children[0].children[0].data == "node_name"
    assert tree.children[0].children[0].children[0].value == "INTENTION"
    assert tree.children[0].children[1].data == "node_multiline_value"
    assert tree.children[0].children[1].children[0].value == "Intention A."


def test_32_two_single_line_fields():
    """
    Ensure that a single field can be parsed.

    It turns out that this particular case is pretty sensitive with respect to
    how the grammar is constructed.
    """

    input_string = """
        STATEMENT: This can likely replace _weak below with no problem.

        STATEMENT: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(input_string, parse_nodes=True)
    assert tree.data == "start"

    assert len(tree.children) == 2
    assert tree.children[0].data == "node_field"
    assert tree.children[0].children[0].data == "node_name"
    assert tree.children[0].children[0].children[0].value == "STATEMENT"
    assert tree.children[0].children[1].data == "node_multiline_value"
    assert (
        tree.children[0].children[1].children[0].value
        == "This can likely replace _weak below with no problem."
    )


def test_32B_two_single_line_fields_consecutive():
    """
    Ensure that two consecutive fields can be parsed.
    """

    input_string = """
        STATEMENT: This can likely replace _weak below with no problem.
        STATEMENTT: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(input_string, parse_nodes=True)

    assert tree.data == "start"

    assert len(tree.children) == 2
    assert tree.children[0].data == "node_field"
    assert tree.children[0].children[0].data == "node_name"
    assert tree.children[0].children[0].children[0].value == "STATEMENT"
    assert tree.children[0].children[1].data == "node_multiline_value"
    assert (
        tree.children[0].children[1].children[0].value
        == "This can likely replace _weak below with no problem."
    )


def test_33_multiline_and_multiparagraph_fields():
    input_string = """\
FOOBAR

STATEMENT: This
           \\n\\n
           is
           \\n\\n
           how we do paragraphs.

FOOBAR
"""

    tree = MarkerLexer.parse(input_string, parse_nodes=True)
    assert tree.data == "start"

    assert len(tree.children) == 1
    assert tree.children[0].data == "node_field"
    assert tree.children[0].children[0].data == "node_name"
    assert tree.children[0].children[0].children[0].value == "STATEMENT"
    assert tree.children[0].children[1].data == "node_multiline_value"
    assert tree.children[0].children[1].children[0].value == "This"
    assert tree.children[0].children[1].children[1].value == "           \\n\\n"
    assert tree.children[0].children[1].children[2].value == "           is"
    assert tree.children[0].children[1].children[3].value == "           \\n\\n"
    assert (
        tree.children[0].children[1].children[4].value
        == "           how we do paragraphs."
    )


def test_60_exclude_reserved_keywords():
    """
    Ensure that a single field can be parsed.

    It turns out that this particular case is pretty sensitive with respect to
    how the grammar is constructed.
    """

    input_string = """
        FIXME: This can likely replace _weak below with no problem.

        TODO: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    assert len(tree.children) == 0
