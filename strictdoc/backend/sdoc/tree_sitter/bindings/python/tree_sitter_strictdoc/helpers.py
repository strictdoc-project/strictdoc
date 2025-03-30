from typing import Generator

import tree_sitter


def print_tree(node, input_content, indent=0):
    if indent == 0:
        print("")
        print(f"INPUT:\n\"\"\"\n{input_content}\n\"\"\"\n")
    print("  " * indent + f"{node.type} ({node.start_point} - {node.end_point})")
    for child in node.children:
        print_tree(child, input_content, indent + 1)
    if indent == 0:
        print("")


def traverse_tree_with_validation(tree: tree_sitter.Tree) -> Generator[
    tree_sitter.Node, None, None]:
    cursor = tree.walk()

    visited_children = False

    while True:
        if cursor.node.type.endswith("_error"):
            if cursor.node.type == "document_error":
                raise RuntimeError(tree, "document_error")
            if cursor.node.type == "document_literal_error":
                raise RuntimeError(tree, "document_literal_error")
            if cursor.node.type == "newline_character_error":
                raise RuntimeError(tree, "newline_character_error")
            if cursor.node.type == "trailing_end_error":
                raise RuntimeError(tree, "trailing_end_error")

            raise NotImplementedError(cursor.node.type)

        if not visited_children:
            yield cursor.node
            if not cursor.goto_first_child():
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break
