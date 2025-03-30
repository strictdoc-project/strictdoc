import pytest

from strictdoc.backend.sdoc.tree_sitter.bindings.python.tree_sitter_strictdoc.helpers import \
    print_tree
from strictdoc.backend.sdoc.tree_sitter.bindings.python.tree_sitter_strictdoc.parser import \
    StrictDocParser


def test__document__basic():
    parser = StrictDocParser()

    input_content = b"[DOCUMENT]\n\n"
    tree = parser.parse(input_content)
    print_tree(tree.root_node, input_content)

    assert tree.root_node.type == "top_node"
    assert tree.root_node.children[0].type == "DOCUMENT"
    assert len(tree.root_node.children[0].children) == 5
    assert tree.root_node.children[0].children[3].type == "newline_character"
    assert tree.root_node.children[0].children[4].type == "newline_character"


def test__document__error__extra_newline():
    parser = StrictDocParser()

    input_content = b"[DOCUMENT]\n\n\n"

    with pytest.raises(RuntimeError) as exc_info:
        parser.parse(input_content)

    assert exc_info.value.args[1] == "trailing_end_error"

    tree = exc_info.value.args[0]
    print_tree(tree.root_node, input_content)

    assert tree.root_node.type == "top_node"
    assert len(tree.root_node.children) == 2
    assert tree.root_node.children[0].type == "DOCUMENT"
    assert len(tree.root_node.children[0].children) == 6
    assert tree.root_node.children[0].children[3].type == "newline_character"
    assert tree.root_node.children[0].children[4].type == "newline_character"
    assert tree.root_node.children[0].children[5].type == "trailing_end_error"

    assert tree.root_node.children[1].type == "EOF"


def test__document__error__empty_spaces():
    parser = StrictDocParser()

    input_content = b"   "

    with pytest.raises(RuntimeError) as exc_info:
        parser.parse(input_content)

    assert exc_info.value.args[1] == "document_error"

    tree = exc_info.value.args[0]
    print_tree(tree.root_node, input_content)


def test__document__error__incomplete_literal():
    parser = StrictDocParser()

    input_content = b"[DOC"

    with pytest.raises(RuntimeError) as exc_info:
        parser.parse(input_content)

    assert exc_info.value.args[1] == "document_literal_error"

    tree = exc_info.value.args[0]
    print_tree(tree.root_node, input_content)

    assert tree.root_node.type == "ERROR"
    assert tree.root_node.children[1].type == "document_literal_error"


def test__document__error__misspelled_literal():
    parser = StrictDocParser()

    input_content = b"[DOC UMENT]"

    with pytest.raises(RuntimeError) as exc_info:
        parser.parse(input_content)

    assert exc_info.value.args[1] == "document_literal_error"

    tree = exc_info.value.args[0]
    print_tree(tree.root_node, input_content)

    assert tree.root_node.type == "ERROR"
    assert tree.root_node.children[1].type == "document_literal_error"


def test__document__error__no_first_newline():
    parser = StrictDocParser()

    input_content = b"[DOCUMENT]"

    with pytest.raises(RuntimeError) as exc_info:
        parser.parse(input_content)

    tree = exc_info.value.args[0]
    print_tree(tree.root_node, input_content)

    assert exc_info.value.args[1] == "newline_character_error"


def test__document__error__only_one_newline():
    parser = StrictDocParser()

    input_content = b"[DOCUMENT]\n"

    with pytest.raises(RuntimeError) as exc_info:
        parser.parse(input_content)

    tree = exc_info.value.args[0]
    print_tree(tree.root_node, input_content)

    assert exc_info.value.args[1] == "newline_character_error"


def test__document__error__space_instead_first_newline():
    parser = StrictDocParser()

    input_content = b"[DOCUMENT] "

    with pytest.raises(RuntimeError) as exc_info:
        parser.parse(input_content)

    tree = exc_info.value.args[0]
    print_tree(tree.root_node, input_content)

    assert exc_info.value.args[1] == "newline_character_error"
