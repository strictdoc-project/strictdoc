from typing import Generator

import tree_sitter
import tree_sitter_strictdoc


def traverse_tree(tree: tree_sitter.Tree) -> Generator[
    tree_sitter.Node, None, None]:
    cursor = tree.walk()

    visited_children = False
    while True:
        if cursor.node.type == "ERROR":
            print(f"Error at {cursor.node.start_point} - {cursor.node.end_point}: {cursor.node}")

        if cursor.node.type != "ERROR" and not visited_children:
            yield cursor.node
            if not cursor.goto_first_child():
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break

def test_can_load_grammar():
    try:
        language = tree_sitter.Language(tree_sitter_strictdoc.language())
    except Exception:
        assert 0

    parser = tree_sitter.Parser(language)

    tree = parser.parse(b"hello")

    # assert 0, tree.root_node  # traverse_tree(tree)
    assert 0, list(traverse_tree(tree))
