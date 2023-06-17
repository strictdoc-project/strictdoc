from typing import Any


def assert_cast(node, node_type) -> Any:
    assert isinstance(node, node_type), (node, node_type)
    return node
