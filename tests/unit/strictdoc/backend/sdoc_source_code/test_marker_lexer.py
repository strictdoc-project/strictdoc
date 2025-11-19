"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

from typing import Any, List, Optional

from lark import Tree

from strictdoc.backend.sdoc_source_code.comment_parser.marker_lexer import (
    MarkerLexer,
)


def lark_tree_find_child_trees(tree: Any) -> List[Any]:
    return list(filter(lambda child_: isinstance(child_, Tree), tree.children))


def assert_relation_marker(
    node: Any, node_uids: List[str], scope: str, role: Optional[str] = None
) -> None:
    relation_marker_trees = lark_tree_find_child_trees(node)
    for idx_ in range(len(node_uids)):
        assert relation_marker_trees[idx_].data == "relation_node_uid"
        assert relation_marker_trees[idx_].children[0].value == node_uids[idx_]

    assert relation_marker_trees[len(node_uids)].data == "relation_scope"
    assert relation_marker_trees[len(node_uids)].children[0].value == scope

    if role is not None:
        assert relation_marker_trees[len(node_uids) + 1].data == "relation_role"
        assert (
            relation_marker_trees[len(node_uids) + 1].children[0].value == role
        )


def assert_node_field(
    node: Any, field_name: str, expected_field_value: List[str]
) -> None:
    node_name = next(node.find_data("node_name"))
    assert node_name.children[0].value == field_name

    node_values = node.find_data("node_multiline_value")
    node_value = next(node_values)

    values = list(
        node_value.scan_values(
            lambda t: t.type
            in ("NODE_FIRST_STRING_VALUE", "NODE_STRING_VALUE", "NEWLINE")
        )
    )
    for idx in range(len(expected_field_value)):
        assert values[idx] == expected_field_value[idx]


def test_01_basic_nominal() -> None:
    tree = MarkerLexer.parse("")
    assert tree.data == "start"


def test_02_single_marker() -> None:
    input_strings = [
        ("REQ-1", "REQ-2"),
        ("REQ_1", "REQ_2"),
        ("REQ.1", "REQ.2"),
        ("REQ/1", "REQ/2"),
    ]
    for node_1_, node_2_ in input_strings:
        input_string = f"@relation({node_1_}, {node_2_}, scope=function)"
        tree = MarkerLexer.parse(input_string)
        assert tree.data == "start"

        relation_markers = tree.find_data("relation_marker")
        relation_marker = next(relation_markers)
        assert relation_marker.data == "relation_marker"

        assert_relation_marker(relation_marker, [node_1_, node_2_], "function")


def test_03_single_marker_with_role() -> None:
    tree = MarkerLexer.parse(
        "@relation(REQ-1, scope=function, role=Implementation)"
    )
    assert tree.data == "start"

    relation_markers = tree.find_data("relation_marker")
    relation_marker = next(relation_markers)
    assert relation_marker.data == "relation_marker"

    assert_relation_marker(
        relation_marker, ["REQ-1"], "function", "Implementation"
    )


def test_04_skip_markers() -> None:
    tree = MarkerLexer.parse("@relation(skip, scope=file)")
    assert tree.data == "start"

    relation_markers = tree.find_data("relation_marker")
    relation_marker = next(relation_markers)
    assert relation_marker.data == "relation_marker"

    assert_relation_marker(
        relation_marker,
        ["skip"],
        "file",
    )


def test_10_single_marker_with_newline() -> None:
    input_string = "@relation(REQ-1, scope=function)\n"

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    relation_markers = tree.find_data("relation_marker")
    relation_marker = next(relation_markers)
    assert relation_marker.data == "relation_marker"

    assert_relation_marker(
        relation_marker,
        ["REQ-1"],
        "function",
    )


def test_11_single_marker_with_newline() -> None:
    input_string = """\
@relation(
    REQ-1,
    scope=function
)
"""

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    relation_markers = tree.find_data("relation_marker")
    relation_marker = next(relation_markers)
    assert relation_marker.data == "relation_marker"

    assert_relation_marker(
        relation_marker,
        ["REQ-1"],
        "function",
    )


def test_12_python_preprocessed_input() -> None:
    input_string = """\
  @relation(REQ-001, REQ-002, REQ-003, scope=range_start)
"""

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    relation_markers = tree.find_data("relation_marker")
    relation_marker = next(relation_markers)
    assert relation_marker.data == "relation_marker"

    assert_relation_marker(
        relation_marker,
        ["REQ-001", "REQ-002", "REQ-003"],
        "range_start",
    )


def test_13_python_preprocessed_input() -> None:
    input_string = """\
  @relation(REQ-001, REQ-002, REQ-003, scope=range_start)
  print("Hello world")
  @relation(REQ-001, REQ-002, REQ-003, scope=range_end)
""".lstrip()

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    relation_markers = tree.find_data("relation_marker")
    relation_marker_0 = next(relation_markers)
    relation_marker_1 = next(relation_markers)

    assert_relation_marker(
        relation_marker_0,
        ["REQ-001", "REQ-002", "REQ-003"],
        "range_start",
    )
    assert_relation_marker(
        relation_marker_1,
        ["REQ-001", "REQ-002", "REQ-003"],
        "range_end",
    )


def test_20_single_marker_and_normal_line() -> None:
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

    relation_markers = tree.find_data("relation_marker")
    relation_marker = next(relation_markers)
    assert_relation_marker(
        relation_marker,
        ["REQ-1"],
        "function",
    )


def test_30_relation_and_field() -> None:
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

Additionally, the system 3 shall do 4.
"""

    tree = MarkerLexer.parse(input_string, custom_tags={"STATEMENT"})
    assert tree.data == "start"

    relation_markers = tree.find_data("relation_marker")
    relation_marker = next(relation_markers)

    assert_relation_marker(
        relation_marker,
        ["REQ-1"],
        "function",
    )

    node_fields = list(tree.find_data("node_field"))

    assert_node_field(
        node_fields[0],
        "STATEMENT",
        ["When C,", "\n", "           The system A shall do B"],
    )

    assert_node_field(
        node_fields[1],
        "STATEMENT",
        ["When Z,", "\n", "           The system X shall do Y"],
    )

    assert_node_field(
        node_fields[2],
        "STATEMENT",
        ["When 1, The system 2 shall do 3"],
    )

    assert_node_field(
        node_fields[3],
        "STATEMENT",
        [
            "When 1, The system 2 shall do 3",
            "\n\n",
            "Additionally, the system 3 shall do 4.",
        ],
    )


def test_31_single_node_field() -> None:
    """
    Ensure that a single field can be parsed.

    It turns out that this particular case is pretty sensitive with respect to
    how the grammar is constructed.
    """

    input_string = """
        STATEMENT: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(input_string, custom_tags={"STATEMENT"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))

    assert_node_field(
        node_fields[0],
        "STATEMENT",
        ["This can likely replace _weak below with no problem."],
    )


def test_31B_single_node_field() -> None:
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

    tree = MarkerLexer.parse(input_string, custom_tags={"INTENTION"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))

    assert_node_field(
        node_fields[0],
        "INTENTION",
        ["Intention A."],
    )


def test_31C_single_node_field() -> None:
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

    tree = MarkerLexer.parse(input_string, custom_tags={"INTENTION"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))

    assert_node_field(
        node_fields[0],
        "INTENTION",
        ["Intention A."],
    )


def test_32_two_single_line_fields() -> None:
    """
    Ensure that a single field can be parsed.

    It turns out that this particular case is pretty sensitive with respect to
    how the grammar is constructed.
    """

    input_string = """
        STATEMENT: This can likely replace _weak below with no problem.

        STATEMENT: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(input_string, custom_tags={"STATEMENT"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))

    assert_node_field(
        node_fields[0],
        "STATEMENT",
        ["This can likely replace _weak below with no problem."],
    )
    assert_node_field(
        node_fields[1],
        "STATEMENT",
        ["This can likely replace _weak below with no problem."],
    )


def test_32B_two_single_line_fields_consecutive() -> None:
    """
    Ensure that two consecutive fields can be parsed.
    """

    input_string = """
        STATEMENT: This can likely replace _weak below with no problem.
        STATEMENTT: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(
        input_string, custom_tags={"STATEMENT", "STATEMENTT"}
    )

    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))

    assert_node_field(
        node_fields[0],
        "STATEMENT",
        ["This can likely replace _weak below with no problem."],
    )
    assert_node_field(
        node_fields[1],
        "STATEMENTT",
        ["This can likely replace _weak below with no problem."],
    )


def test_33_multiline_and_multiparagraph_fields() -> None:
    input_string = """\
FOOBAR

STATEMENT: This

           is

           how we do paragraphs.
"""

    tree = MarkerLexer.parse(input_string, custom_tags={"STATEMENT"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))

    assert_node_field(
        node_fields[0],
        "STATEMENT",
        [
            "This",
            "\n\n",
            "           is",
            "\n\n",
            "           how we do paragraphs.",
        ],
    )


def test_34_node_text_starting_below() -> None:
    """
    Ensure that first text can start somewhere in the next lines after a field,
    and that the result keeps starting newlines as separate NEWLINE-symbol.
    """
    input_string = """\
FIELD1:

   Text starting far off from tag.
"""
    tree = MarkerLexer.parse(input_string, custom_tags={"FIELD1"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))
    assert len(node_fields) == 1

    assert_node_field(
        node_fields[0],
        "FIELD1",
        [
            "\n\n",
            "   Text starting far off from tag.",
            "\n",
        ],
    )


def test_60_exclude_reserved_keywords() -> None:
    input_string = """
        FIXME: This can likely replace _weak below with no problem.

        TODO: This can likely replace _weak below with no problem.
    """

    tree = MarkerLexer.parse(input_string)
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))
    assert len(node_fields) == 0


def test_70_exclude_similar_but_not_in_grammar() -> None:
    input_string = """
        Note: This is ordinary comment text.

        STATEMENT: This can likely replace _weak below with no problem.
        FYI: More ordinary comment text.

        TEST: This can likely replace _weak below with no problem.

        Hint: Again, ordinary comment text.
    """

    tree = MarkerLexer.parse(input_string, custom_tags={"STATEMENT", "TEST"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))
    assert len(node_fields) == 2

    assert_node_field(
        node_fields[0],
        "STATEMENT",
        ["This can likely replace _weak below with no problem."],
    )
    assert_node_field(
        node_fields[1],
        "TEST",
        ["This can likely replace _weak below with no problem."],
    )


def test_80_linux_spdx_like_identifiers() -> None:
    input_string = """\
SPDX-ID: REQ-1

SPDX-Text: This
           is
           a statement

           And this is the same statement's another paragraph.
"""

    tree = MarkerLexer.parse(input_string, custom_tags={"SPDX-ID", "SPDX-Text"})
    assert tree.data == "start"

    node_fields = list(tree.find_data("node_field"))
    assert len(node_fields) == 2

    assert_node_field(
        node_fields[0],
        "SPDX-ID",
        ["REQ-1"],
    )
    assert_node_field(
        node_fields[1],
        "SPDX-Text",
        [
            "This",
            "\n",
            "           is",
            "\n",
            "           a statement",
            "\n\n",
            "           And this is the same statement's another paragraph.",
        ],
    )
