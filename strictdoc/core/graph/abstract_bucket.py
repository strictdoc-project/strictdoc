# mypy: disable-error-code="no-untyped-def"
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from strictdoc.helpers.ordered_set import OrderedSet

ALL_EDGES = ".all"


class AbstractBucket(ABC):
    @abstractmethod
    def has_link(self, *, lhs_node: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_link_value(
        self, *, lhs_node: Any, edge: Optional[str] = None
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_link_value_weak(self, *, lhs_node: Any) -> Optional[Any]:
        raise NotImplementedError

    def get_link_values(
        self, *, lhs_node: Any, edge: Optional[str] = None
    ) -> OrderedSet[Any]:
        raise NotImplementedError

    def get_link_values_with_edges(
        self, *, lhs_node: Any, edge: Optional[str] = None
    ) -> List[Tuple[Any, Optional[str]]]:
        raise NotImplementedError

    def get_link_values_reverse(self, *, rhs_node: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_link(
        self, *, lhs_node: Any, rhs_node: Any, edge: Optional[str] = None
    ):
        raise NotImplementedError

    @abstractmethod
    def delete_link(
        self, *, lhs_node: Any, rhs_node: Any, edge: Optional[str] = None
    ):
        raise NotImplementedError

    def delete_link_weak(
        self,
        *,
        lhs_node: Any,
        rhs_node: Any,
    ):
        raise NotImplementedError

    def delete_all_links(
        self,
        *,
        lhs_node: Any,
    ):
        raise NotImplementedError
