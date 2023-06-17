from collections import defaultdict
from typing import Any, Dict, Optional, Set

from strictdoc.helpers.uuid import create_uuid


class ConstraintViolation(Exception):
    def __init__(self, message):
        super().__init__(message)


class UUID(str):
    @staticmethod
    def create() -> "UUID":
        return UUID(create_uuid())


class LinkType:
    pass


def link_dict():
    return defaultdict(set)


class GraphDatabase:
    def __init__(self):
        self.nodes: Dict[UUID, Any] = {}
        self.links: Dict[LinkType, Dict[UUID, Set[UUID]]] = defaultdict(
            link_dict
        )
        self.links_reverse: Dict[LinkType, Dict[UUID, Set[UUID]]] = defaultdict(
            link_dict
        )

        # Attachable validation classes.
        self.remove_node_validation = None

    def add_node(self, uuid: UUID, node: Any):
        assert uuid not in self.nodes, (self.nodes, node)
        self.nodes[uuid] = node

    def get_node(self, uuid: UUID) -> Any:
        if uuid not in self.nodes:
            raise LookupError
        return self.nodes[uuid]

    def get_node_weak(self, uuid: UUID) -> Optional[Any]:
        if uuid not in self.nodes:
            return None
        return self.nodes[uuid]

    def remove_node(self, uuid: UUID):
        if uuid not in self.nodes:
            raise LookupError
        if self.remove_node_validation is not None:
            self.remove_node_validation.validate(self, uuid)
        del self.nodes[uuid]

    def get_link_values(
        self, *, link_type: LinkType, lhs_node: Any
    ) -> Set[Any]:
        if link_type not in self.links:
            raise LookupError
        links = self.links[link_type]
        if lhs_node not in links:
            raise LookupError
        link_values = self.links[link_type][lhs_node]
        if len(link_values) == 0:
            raise LookupError
        return link_values

    def get_link_value(self, *, link_type: LinkType, lhs_node: Any) -> Any:
        link_values = self.get_link_values(
            link_type=link_type, lhs_node=lhs_node
        )
        assert len(link_values) == 1
        return next(iter(link_values))

    def get_link_value_weak(
        self, *, link_type: LinkType, lhs_node: Any
    ) -> Optional[Any]:
        link_values = self.get_link_values_weak(
            link_type=link_type, lhs_node=lhs_node
        )
        if link_values is not None and len(link_values) > 0:
            assert len(link_values) == 1
            return next(iter(link_values))
        return None

    def get_link_values_weak(
        self, *, link_type: LinkType, lhs_node: Any
    ) -> Optional[Set[Any]]:
        if link_type not in self.links:
            return None
        links = self.links[link_type]
        if lhs_node not in links:
            return None
        return self.links[link_type][lhs_node]

    def link_exists(self, *, link_type: LinkType, lhs_node: Any) -> bool:
        if link_type not in self.links:
            return False
        links = self.links[link_type]
        if lhs_node not in links:
            return False
        return True

    def add_link(self, *, link_type: LinkType, lhs_node: Any, rhs_node: Any):
        assert lhs_node != rhs_node
        links = self.links[link_type]
        if lhs_node in links:
            assert rhs_node not in links[lhs_node]

        self.links[link_type][lhs_node].add(rhs_node)
        self.links_reverse[link_type][rhs_node].add(lhs_node)

    def remove_link(self, *, link_type: LinkType, lhs_node: Any, rhs_node: Any):
        assert link_type in self.links
        assert lhs_node in self.links[link_type]
        self.links[link_type][lhs_node].remove(rhs_node)
        self.links_reverse[link_type][rhs_node].remove(lhs_node)
