# mypy: disable-error-code="no-untyped-def,type-arg"
from copy import copy
from typing import Any, Dict, Optional

from strictdoc.core.graph.abstract_bucket import AbstractBucket
from strictdoc.helpers.ordered_set import OrderedSet


class ManyToManySet(AbstractBucket):
    def __init__(self, lhs_type: type, rhs_type: type):
        self._links: Dict[Any, OrderedSet[Any]] = {}
        self._links_reverse: Dict[Any, OrderedSet[Any]] = {}
        self._lhs_type: type = lhs_type
        self._rhs_type: type = rhs_type

    def has_link(self, *, lhs_node: Any) -> bool:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        return lhs_node in self._links

    def get_count(self) -> Any:
        return len(self._links)

    def reverse_count(self) -> Any:
        return len(self._links_reverse)

    def get_link_value(self, *, lhs_node: Any) -> Any:
        raise NotImplementedError

    def get_link_value_weak(self, *, lhs_node: Any) -> Any:
        raise NotImplementedError

    def get_link_values_weak(self, *, lhs_node: Any) -> Optional[Any]:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        return self._links.get(lhs_node, None)

    def get_link_values(self, *, lhs_node: Any) -> Any:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        return self._links[lhs_node]

    def get_link_values_reverse_weak(
        self, *, rhs_node: Any
    ) -> Optional[OrderedSet]:
        assert isinstance(rhs_node, self._rhs_type), rhs_node
        return self._links_reverse.get(rhs_node, None)

    def get_link_values_reverse(self, *, rhs_node: Any) -> OrderedSet:
        assert isinstance(rhs_node, self._rhs_type), rhs_node
        return self._links_reverse[rhs_node]

    def create_link(self, *, lhs_node: Any, rhs_node: Any) -> None:
        if not isinstance(lhs_node, self._lhs_type):
            raise TypeError(
                f"LHS type mismatch: {type(lhs_node)} is not of {self._lhs_type}"
            )
        if not isinstance(rhs_node, self._rhs_type):
            raise TypeError(
                f"RHS type mismatch: {type(rhs_node)} is not of {self._rhs_type}"
            )
        assert lhs_node != rhs_node, (lhs_node, rhs_node)

        lhs_node_links = self._links.setdefault(lhs_node, OrderedSet())
        assert rhs_node not in lhs_node_links
        lhs_node_links.add(rhs_node)

        rhs_node_links = self._links_reverse.setdefault(rhs_node, OrderedSet())
        assert lhs_node not in rhs_node_links
        rhs_node_links.add(lhs_node)

    def create_link_weak(self, *, lhs_node: Any, rhs_node: Any) -> None:
        if not isinstance(lhs_node, self._lhs_type):
            raise TypeError(
                f"LHS type mismatch: {type(lhs_node)} is not of {self._lhs_type}"
            )
        if not isinstance(rhs_node, self._rhs_type):
            raise TypeError(
                f"RHS type mismatch: {type(rhs_node)} is not of {self._rhs_type}"
            )
        assert lhs_node != rhs_node, (lhs_node, rhs_node)

        lhs_node_links = self._links.setdefault(lhs_node, OrderedSet())
        lhs_node_links.add(rhs_node)

        rhs_node_links = self._links_reverse.setdefault(rhs_node, OrderedSet())
        rhs_node_links.add(lhs_node)

    def delete_link(
        self,
        *,
        lhs_node: Any,
        rhs_node: Any,
    ):
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        assert isinstance(rhs_node, self._rhs_type), rhs_node

        assert lhs_node in self._links
        assert rhs_node in self._links_reverse

        self._links[lhs_node].remove(rhs_node)

        rhs_links = self._links_reverse[rhs_node]
        rhs_links.remove(lhs_node)
        if len(rhs_links) == 0:
            del self._links_reverse[rhs_node]

    def delete_link_weak(
        self,
        *,
        lhs_node: Any,
        rhs_node: Any,
    ):
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        assert isinstance(rhs_node, self._rhs_type), rhs_node

        if lhs_node in self._links:
            lhs_links = self._links[lhs_node]
            lhs_links.discard(rhs_node)
            if len(lhs_links) == 0:
                del self._links[lhs_node]

        if rhs_node in self._links_reverse:
            rhs_links = self._links_reverse[rhs_node]
            rhs_links.discard(lhs_node)
            if len(rhs_links) == 0:
                del self._links_reverse[rhs_node]

    def delete_all_links(
        self,
        *,
        lhs_node: Any,
    ):
        assert isinstance(lhs_node, self._lhs_type), lhs_node

        assert lhs_node in self._links

        del self._links[lhs_node]

        for existing_rhs_node_ in copy(self._links_reverse):
            existing_rhs_node_links = self._links_reverse[existing_rhs_node_]
            existing_rhs_node_links.remove(lhs_node)
            if len(existing_rhs_node_links) == 0:
                del self._links_reverse[existing_rhs_node_]
