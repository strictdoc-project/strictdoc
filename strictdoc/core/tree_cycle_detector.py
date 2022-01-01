from collections import deque

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError

BEFORE = 1
AFTER = 2


class TreeCycleDetector:
    def __init__(self, whitelisted_nodes):
        assert isinstance(whitelisted_nodes, object)
        self.checked = set()
        self.whitelisted_nodes = whitelisted_nodes

    def check_node(self, node, links_function):
        if node in self.checked:
            return
        stack = deque()
        stack.append((node, BEFORE))
        visited = set()
        while stack:
            current_node, token = stack[-1]
            if current_node not in self.whitelisted_nodes:
                stack.pop()
                continue
            if token == BEFORE:
                visited.add(current_node)
                stack[-1] = (current_node, AFTER)
                node_links = links_function(current_node)
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
