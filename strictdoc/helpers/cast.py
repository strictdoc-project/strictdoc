# mypy: disable-error-code="no-untyped-def"
from typing import Any, Optional


def assert_cast(node, node_type) -> Any:
    assert isinstance(node, node_type), (node, node_type)
    return node


def assert_optional_cast(node: Optional[Any], node_type) -> Optional[Any]:
    if node is not None:
        assert isinstance(node, node_type), (node, node_type)
        return node
    return None
