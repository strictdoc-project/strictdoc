# mypy: disable-error-code="no-untyped-def"
from typing import Any, Dict, Hashable, List, Optional, Tuple

from strictdoc.core.graph.abstract_bucket import AbstractBucket
from strictdoc.helpers.ordered_set import OrderedSet


class ConstraintViolation(Exception):
    def __init__(self, message):
        super().__init__(message)


class GraphDatabase:
    def __init__(self, buckets: List[Tuple[Any, AbstractBucket]]):
        self._links = None
        self._id_to_bucket: Dict[Any, AbstractBucket] = {}
        for bucket_ in buckets:
            assert bucket_[0] not in self._id_to_bucket
            self._id_to_bucket[bucket_[0]] = bucket_[1]

    def has_link(self, *, link_type: Hashable, lhs_node: Any) -> bool:
        return self._id_to_bucket[link_type].has_link(lhs_node=lhs_node)

    def get_count(self, *, link_type: Hashable) -> int:
        return self._id_to_bucket[link_type].get_count()

    def get_link_value_weak(
        self, *, link_type: Hashable, lhs_node: Any
    ) -> Optional[Any]:
        return self._id_to_bucket[link_type].get_link_value_weak(
            lhs_node=lhs_node
        )

    def get_link_value(
        self, *, link_type: Hashable, lhs_node: Any, edge: Optional[str] = None
    ) -> Any:
        return self._id_to_bucket[link_type].get_link_value(
            lhs_node=lhs_node, edge=edge
        )

    def get_link_values(
        self, *, link_type: Hashable, lhs_node: Any, edge: Optional[str] = None
    ) -> OrderedSet[Any]:
        return self._id_to_bucket[link_type].get_link_values(
            lhs_node=lhs_node, edge=edge
        )

    def get_link_values_with_edges(
        self, *, link_type: Hashable, lhs_node: Any, edge: Optional[str] = None
    ) -> List[Tuple[Any, Optional[str]]]:
        return self._id_to_bucket[link_type].get_link_values_with_edges(
            lhs_node=lhs_node, edge=edge
        )

    def get_link_values_reverse(
        self, *, link_type: Hashable, rhs_node: Any
    ) -> Any:
        return self._id_to_bucket[link_type].get_link_values_reverse(
            rhs_node=rhs_node
        )

    def create_link(
        self,
        *,
        link_type: Hashable,
        lhs_node: Any,
        rhs_node: Any,
        edge: Optional[str] = None,
    ):
        assert lhs_node is not None, lhs_node
        assert rhs_node is not None, rhs_node
        self._id_to_bucket[link_type].create_link(
            lhs_node=lhs_node, rhs_node=rhs_node, edge=edge
        )

    def delete_link(
        self,
        *,
        link_type: Hashable,
        lhs_node: Any,
        rhs_node: Any,
        edge: Optional[str] = None,
    ):
        self._id_to_bucket[link_type].delete_link(
            lhs_node=lhs_node, rhs_node=rhs_node, edge=edge
        )

    def delete_link_weak(
        self,
        *,
        link_type: Hashable,
        lhs_node: Any,
        rhs_node: Any,
    ):
        self._id_to_bucket[link_type].delete_link_weak(
            lhs_node=lhs_node, rhs_node=rhs_node
        )

    def delete_all_links(
        self,
        *,
        link_type: Hashable,
        lhs_node: Any,
    ):
        self._id_to_bucket[link_type].delete_all_links(lhs_node=lhs_node)
