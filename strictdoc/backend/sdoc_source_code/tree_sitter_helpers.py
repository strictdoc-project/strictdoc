from typing import Generator, Optional, Tuple, Union

from tree_sitter import Node, Tree


def traverse_tree(tree: Tree) -> Generator[Node, None, None]:
    cursor = tree.walk()

    visited_children = False
    while True:
        if not visited_children:
            yield cursor.node
            if not cursor.goto_first_child():
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break


def ts_find_child_node_by_type(
    node: Node, node_type: Union[str, Tuple[str, ...], str]
) -> Optional[Node]:
    node_types: Tuple[str, ...] = (
        node_type if isinstance(node_type, tuple) else (node_type,)
    )
    for child_ in node.children:
        if child_.type in node_types:
            return child_
    return None


def ts_find_child_nodes_by_type(
    node: Node, node_type: str
) -> Generator[Node, None, None]:
    for child_ in node.children:
        if child_.type == node_type:
            yield child_
