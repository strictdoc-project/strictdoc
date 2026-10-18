"""
@relation(SDOC-SRS-142, scope=file)
"""

from typing import Generator, Optional, Tuple, Union

from tree_sitter import Node, Tree


def traverse_tree(tree: Tree) -> Generator[Node, None, None]:
    cursor = tree.walk()

    visited_children = False
    while True:
        if not visited_children:
            if cursor.node is not None:
                yield cursor.node
            if not cursor.goto_first_child():
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break


def ts_find_child_node_by_type(
    node: Node,
    node_type: Union[str, Tuple[str, ...], str],
    raise_on_error: bool = False,
) -> Optional[Node]:
    node_types: Tuple[str, ...] = (
        node_type if isinstance(node_type, tuple) else (node_type,)
    )
    for child_ in node.children:
        if child_.type in node_types:
            return child_
        elif (
            raise_on_error
            and child_.type == "ERROR"
            and not _ts_is_identifier_only_error_node(child_)
        ):
            raise LookupError("stop search on error node")
    return None


def ts_find_child_nodes_by_type(
    node: Node, node_type: str
) -> Generator[Node, None, None]:
    for child_ in node.children:
        if child_.type == node_type:
            yield child_


def _ts_is_identifier_only_error_node(node: Node) -> bool:
    """
    Check if an ERROR node contains only identifiers.

    Tree-sitter creates such a node for "MY_ATTR void foo(void) { }": it
    takes MY_ATTR as the return type and puts "void" into the ERROR node.
    """
    assert node.type == "ERROR"
    return node.child_count > 0 and all(
        child_.type == "identifier" for child_ in node.children
    )
