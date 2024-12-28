from copy import copy
from typing import Any, Dict, List, Optional, Tuple

from strictdoc.core.graph.abstract_bucket import ALL_EDGES, AbstractBucket
from strictdoc.helpers.ordered_set import OrderedSet


class ManyToManySet(AbstractBucket):
    def __init__(self, lhs_type: type, rhs_type: type) -> None:
        self._links: Dict[Any, Dict[Optional[str], OrderedSet[Any]]] = {}
        self._links_reverse: Dict[
            Any, Dict[Optional[str], OrderedSet[Any]]
        ] = {}
        self._lhs_type: type = lhs_type
        self._rhs_type: type = rhs_type

    def has_link(self, *, lhs_node: Any) -> bool:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        return lhs_node in self._links

    def get_count(self, edge: Optional[str] = None) -> int:
        total_count = 0
        for _, lhs_node_links in self._links.items():
            for edge_, lhs_node_edge_links_ in lhs_node_links.items():
                if edge in (ALL_EDGES, edge_):
                    total_count += len(lhs_node_edge_links_)
        return total_count

    def get_link_value(
        self, *, lhs_node: Any, edge: Optional[str] = None
    ) -> Any:
        raise NotImplementedError

    def get_link_value_weak(self, *, lhs_node: Any) -> Any:
        raise NotImplementedError

    def get_link_values(
        self, *, lhs_node: Any, edge: Optional[str] = ALL_EDGES
    ) -> OrderedSet[Any]:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        if edge == ALL_EDGES:
            all_values: OrderedSet[Any] = OrderedSet()
            for _, edge_links_ in self._links.setdefault(lhs_node, {}).items():
                for edge_link_ in edge_links_:
                    all_values.add(edge_link_)
            return all_values
        else:
            return self._links.setdefault(lhs_node, {}).setdefault(
                edge, OrderedSet()
            )

    def get_link_values_with_edges(
        self, *, lhs_node: Any, edge: Optional[str] = ALL_EDGES
    ) -> List[Tuple[Any, Optional[str]]]:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        all_values: List[Tuple[Any, Optional[str]]] = []
        for edge_, edge_links_ in self._links.setdefault(lhs_node, {}).items():
            if edge in (ALL_EDGES, edge_):
                for edge_link_ in edge_links_:
                    all_values.append((edge_link_, edge_))
        return all_values

    def get_link_values_reverse(
        self, *, rhs_node: Any, edge: Optional[str] = ALL_EDGES
    ) -> OrderedSet[Any]:
        assert isinstance(rhs_node, self._rhs_type), rhs_node
        if edge == ALL_EDGES:
            all_values: OrderedSet[Any] = OrderedSet()
            for _, edge_links_ in self._links_reverse.setdefault(
                rhs_node, {}
            ).items():
                for edge_link_ in edge_links_:
                    all_values.add(edge_link_)
            return all_values
        return self._links_reverse.setdefault(rhs_node, {}).setdefault(
            edge, OrderedSet()
        )

    def create_link(
        self, *, lhs_node: Any, rhs_node: Any, edge: Optional[str] = None
    ) -> None:
        assert edge != ALL_EDGES
        if not isinstance(lhs_node, self._lhs_type):
            raise TypeError(
                f"LHS type mismatch: {type(lhs_node)} is not of {self._lhs_type}"
            )
        if not isinstance(rhs_node, self._rhs_type):
            raise TypeError(
                f"RHS type mismatch: {type(rhs_node)} is not of {self._rhs_type}"
            )
        assert lhs_node != rhs_node, (lhs_node, rhs_node)

        lhs_node_links = self._links.setdefault(lhs_node, {})
        lhs_node_links_for_edge = lhs_node_links.setdefault(edge, OrderedSet())

        assert rhs_node not in lhs_node_links_for_edge
        lhs_node_links_for_edge.add(rhs_node)

        rhs_node_links = self._links_reverse.setdefault(rhs_node, {})
        rhs_node_links_for_edge = rhs_node_links.setdefault(edge, OrderedSet())
        assert lhs_node not in rhs_node_links_for_edge
        rhs_node_links_for_edge.add(lhs_node)

    def create_link_weak(
        self, *, lhs_node: Any, rhs_node: Any, edge: Optional[str] = None
    ) -> None:
        assert edge != ALL_EDGES
        if not isinstance(lhs_node, self._lhs_type):
            raise TypeError(
                f"LHS type mismatch: {type(lhs_node)} is not of {self._lhs_type}"
            )
        if not isinstance(rhs_node, self._rhs_type):
            raise TypeError(
                f"RHS type mismatch: {type(rhs_node)} is not of {self._rhs_type}"
            )
        assert lhs_node != rhs_node, (lhs_node, rhs_node)

        lhs_node_links = self._links.setdefault(lhs_node, {})
        lhs_node_links_for_edge = lhs_node_links.setdefault(edge, OrderedSet())
        lhs_node_links_for_edge.add(rhs_node)

        rhs_node_links = self._links_reverse.setdefault(rhs_node, {})
        rhs_node_links_for_edge = rhs_node_links.setdefault(edge, OrderedSet())
        rhs_node_links_for_edge.add(lhs_node)

    def delete_link(
        self,
        *,
        lhs_node: Any,
        rhs_node: Any,
        edge: Optional[str] = ALL_EDGES,
    ) -> None:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        assert isinstance(rhs_node, self._rhs_type), rhs_node

        assert lhs_node in self._links
        assert rhs_node in self._links_reverse

        lhs_node_links = self._links[lhs_node]
        if edge == ALL_EDGES:
            for _, edge_links_ in lhs_node_links.items():
                edge_links_.discard(rhs_node)
        else:
            assert edge in lhs_node_links
            lhs_node_links[edge].remove(rhs_node)

        rhs_node_links = self._links_reverse[rhs_node]
        if edge == ALL_EDGES:
            for _, edge_links_ in rhs_node_links.items():
                edge_links_.discard(lhs_node)
        else:
            assert edge in rhs_node_links
            rhs_node_links[edge].remove(lhs_node)

    def delete_link_weak(
        self, *, lhs_node: Any, rhs_node: Any, edge: Optional[str] = ALL_EDGES
    ) -> None:
        assert isinstance(lhs_node, self._lhs_type), lhs_node
        assert isinstance(rhs_node, self._rhs_type), rhs_node

        if lhs_node in self._links:
            lhs_node_links = self._links.get(lhs_node, {})
            if edge == ALL_EDGES:
                for _, edge_links_ in lhs_node_links.items():
                    edge_links_.discard(rhs_node)
            else:
                lhs_node_links_for_edge = lhs_node_links.get(edge, OrderedSet())
                lhs_node_links_for_edge.discard(rhs_node)

        if rhs_node in self._links_reverse:
            rhs_node_links = self._links_reverse.get(rhs_node, {})
            if edge == ALL_EDGES:
                for _, edge_links_ in rhs_node_links.items():
                    edge_links_.discard(lhs_node)
            else:
                rhs_node_links_for_edge = rhs_node_links.get(edge, OrderedSet())
                rhs_node_links_for_edge.discard(lhs_node)

    def delete_all_links(
        self,
        *,
        lhs_node: Any,
    ) -> None:
        assert isinstance(lhs_node, self._lhs_type), lhs_node

        assert lhs_node in self._links

        del self._links[lhs_node]

        for existing_rhs_node_ in copy(self._links_reverse):
            existing_rhs_node_links = self._links_reverse[existing_rhs_node_]
            for _, edge_links_ in existing_rhs_node_links.items():
                edge_links_.discard(lhs_node)
