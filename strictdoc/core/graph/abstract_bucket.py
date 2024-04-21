# mypy: disable-error-code="no-untyped-def"
from abc import ABC, abstractmethod
from typing import Any, Optional


class AbstractBucket(ABC):
    @abstractmethod
    def has_link(self, *, lhs_node: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_count(self) -> Any:
        raise NotImplementedError

    def get_reverse_count(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_link_value(self, *, lhs_node: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_link_value_weak(self, *, lhs_node: Any) -> Optional[Any]:
        raise NotImplementedError

    def get_link_values_weak(self, *, lhs_node: Any) -> Optional[Any]:
        raise NotImplementedError

    def get_link_values(self, *, lhs_node: Any) -> Any:
        raise NotImplementedError

    def get_link_values_reverse_weak(self, *, rhs_node: Any) -> Optional[Any]:
        raise NotImplementedError

    def get_link_values_reverse(self, *, rhs_node: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_link(self, *, lhs_node: Any, rhs_node: Any):
        raise NotImplementedError

    @abstractmethod
    def create_link_weak(self, *, lhs_node: Any, rhs_node: Any):
        raise NotImplementedError

    @abstractmethod
    def delete_link(
        self,
        *,
        lhs_node: Any,
        rhs_node: Any,
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
