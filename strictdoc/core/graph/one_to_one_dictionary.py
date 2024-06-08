# mypy: disable-error-code="no-untyped-def,type-arg"
from typing import Any, Dict, Optional, Tuple, Type, Union

from strictdoc.core.graph.abstract_bucket import AbstractBucket


class OneToOneDictionary(AbstractBucket):
    def __init__(self, lhs_type: Type, rhs_type: Union[Type, Tuple]):
        self._dict: Dict = {}
        self._lhs_type: Type = lhs_type
        self._rhs_type: Union[Type, Tuple] = rhs_type

    def has_link(self, *, lhs_node: Any) -> bool:
        assert isinstance(lhs_node, self._lhs_type), (lhs_node, self._lhs_type)
        return lhs_node in self._dict

    def get_count(self) -> Any:
        return len(self._dict)

    def get_link_value(self, *, lhs_node: Any) -> Any:
        assert isinstance(lhs_node, self._lhs_type)
        return self._dict[lhs_node]

    def get_link_value_weak(self, *, lhs_node: Any) -> Optional[Any]:
        assert isinstance(lhs_node, self._lhs_type)
        return self._dict.get(lhs_node, None)

    def create_link(self, *, lhs_node: Any, rhs_node: Any):
        assert isinstance(lhs_node, self._lhs_type), (lhs_node, self._lhs_type)
        assert isinstance(rhs_node, self._rhs_type), (rhs_node, self._rhs_type)
        assert (
            lhs_node not in self._dict
        ), f"OneToOneDictionary: Cannot create a link because lhs_node already exists: {lhs_node}."
        self._dict[lhs_node] = rhs_node

    def create_link_weak(self, *, lhs_node: Any, rhs_node: Any):
        assert isinstance(lhs_node, self._lhs_type), (lhs_node, self._lhs_type)
        assert isinstance(rhs_node, self._rhs_type), (rhs_node, self._rhs_type)
        self._dict[lhs_node] = rhs_node

    def delete_link(
        self,
        *,
        lhs_node: Any,
        rhs_node: Any,
    ):
        assert isinstance(lhs_node, self._lhs_type), (lhs_node, self._lhs_type)
        assert isinstance(rhs_node, self._rhs_type), (rhs_node, self._rhs_type)
        assert lhs_node in self._dict
        del self._dict[lhs_node]
