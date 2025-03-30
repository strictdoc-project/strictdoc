import pytest

from strictdoc.backend.sdoc.tree_sitter.bindings.python.tree_sitter_strictdoc.helpers import \
    print_tree
from strictdoc.backend.sdoc.tree_sitter.bindings.python.tree_sitter_strictdoc.parser import \
    StrictDocParser
from strictdoc.backend.sdoc_source_code.tree_sitter_helpers import \
    ts_find_child_node_by_type, ts_find_child_nodes_by_type


def test__node__basic():
    parser = StrictDocParser()

    input_content = b"""\
[DOCUMENT]

[NODE]
STATEMENT: FOO1

[NODE]
STATEMENT: FOO2

[NODE]
STATEMENT: FOO3

"""

    tree = parser.parse(input_content)
    print_tree(tree.root_node, input_content)

    assert tree.root_node.type == "top_node"
    assert len(tree.root_node.children) == 2

    assert tree.root_node.children[0].type == "DOCUMENT"
    assert len(tree.root_node.children[0].children) == 8
    assert tree.root_node.children[0].children[3].type == "newline_character"
    assert tree.root_node.children[0].children[4].type == "newline_character"
    assert tree.root_node.children[0].children[5].type == "NODE"
    assert tree.root_node.children[0].children[6].type == "NODE"
    assert tree.root_node.children[0].children[7].type == "NODE"


def test__node__multiline():
    parser = StrictDocParser()

    input_content = b"""\
[DOCUMENT]

[NODE]
STATEMENT: >>>
FOO1
FOO2
FOO3
<<<

[NODE]
STATEMENT: >>>
BAR1
BAR2
BAR3
<<<

[NODE]
STATEMENT: >>>
BAZ1
BAZ2
BAZ3
<<<

"""

    tree = parser.parse(input_content)
    print_tree(tree.root_node, input_content)

    assert tree.root_node.type == "top_node"
    assert len(tree.root_node.children) == 2

    assert tree.root_node.children[0].type == "DOCUMENT"
    assert len(tree.root_node.children[0].children) == 8
    assert tree.root_node.children[0].children[3].type == "newline_character"
    assert tree.root_node.children[0].children[4].type == "newline_character"
    assert tree.root_node.children[0].children[5].type == "NODE"
    assert tree.root_node.children[0].children[6].type == "NODE"
    assert tree.root_node.children[0].children[7].type == "NODE"

    print_tree(tree.root_node.children[0].children[5], input_content)

    multiline_field_nodes = list(ts_find_child_nodes_by_type(tree.root_node.children[0].children[5], "NODE_FIELD_MULTILINE"))
    assert len(multiline_field_nodes) == 1

    multiline_field_values = list(ts_find_child_nodes_by_type(multiline_field_nodes[0], "single_line_string"))
    assert multiline_field_values[0].text == b"FOO1\n"
    assert multiline_field_values[1].text == b"FOO2\n"
    assert multiline_field_values[2].text == b"FOO3\n"
