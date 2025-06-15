from collections import deque
from typing import Callable, Deque, List, Set, Tuple

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError

BEFORE = 1
AFTER = 2


class TreeCycleDetector:
    def __init__(self) -> None:
        self.checked: Set[str] = set()

    def check_node(
        self, node: str, links_function: Callable[[str], List[str]]
    ) -> None:
        if node in self.checked:
            return
        stack: Deque[Tuple[str, int]] = deque()
        stack.append((node, BEFORE))
        visited: Set[str] = set()
        while stack:
            current_node, token = stack[-1]
            if token == BEFORE:
                visited.add(current_node)
                stack[-1] = (current_node, AFTER)
                node_links: List[str] = links_function(current_node)
                for node_link in reversed(node_links):
                    if node_link in visited:
                        cycled_nodes = []
                        for uid, token in stack:
                            if token == BEFORE:
                                continue
                            cycled_nodes.append(uid)
                        raise DocumentTreeError.cycle_error(
                            node_link, cycled_nodes
                        )
                    if node_link not in self.checked:
                        stack.append((node_link, BEFORE))
            elif token == AFTER:
                visited.remove(current_node)
                self.checked.add(current_node)
                stack.pop()
        self.checked.add(node)


class SingleShotTreeCycleDetector:
    def check_node(
        self,
        new_uid: str,
        node: str,
        links_function: Callable[[str], List[str]],
    ) -> None:
        """
        Detect if a new node creates a cycle in the traceability index.

        FIXME: Both cycle detector classes are very similar. Find a way to merge
               them. The added value of this 'single shot' detector is that it
               checks for cycles possibly added by a new node.
        """

        checked: Set[str] = set()

        stack: Deque[Tuple[str, int]] = deque()
        stack.append((node, BEFORE))
        visited = {new_uid}
        while stack:
            current_node, token = stack[-1]
            if token == BEFORE:
                visited.add(current_node)
                stack[-1] = (current_node, AFTER)
                node_links = links_function(current_node)
                for node_link in reversed(node_links):
                    if node_link in visited:
                        cycled_nodes = [new_uid]
                        for uid, token in stack:
                            if token == BEFORE:
                                continue
                            cycled_nodes.append(uid)
                        raise DocumentTreeError.cycle_error(
                            node_link, cycled_nodes
                        )
                    if node_link not in checked:
                        stack.append((node_link, BEFORE))
            elif token == AFTER:
                visited.remove(current_node)
                checked.add(current_node)
                stack.pop()
