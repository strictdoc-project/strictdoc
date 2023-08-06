from collections import defaultdict
from enum import IntEnum
from typing import Any, Dict, List, Optional

from strictdoc.helpers.mid import MID
from strictdoc.helpers.ordered_set import OrderedSet


class ConstraintViolation(Exception):
    def __init__(self, message):
        super().__init__(message)


class LinkType(IntEnum):
    pass


class GraphDatabase:
    def __init__(self):
        self._map_mid_to_node: Dict[MID, Any] = {}
        self._map_uid_to_node: Dict[str, Any] = {}
        self._links: Dict[LinkType, Dict[MID, OrderedSet[MID]]] = defaultdict(
            dict
        )
        self._links_reverse: Dict[
            LinkType, Dict[MID, OrderedSet[MID]]
        ] = defaultdict(dict)

        # Attachable validation classes.
        self.remove_node_validation = None

    def dump(self) -> str:
        result = ""
        result += "=======================\n"
        result += "= Graph database dump =\n"
        result += "=======================\n"

        result += "Direct links:\n"
        for link_type, links in self._links.items():
            result += f"Link type: {link_type.name}\n"
            for lhs_mid, rhs_mids in links.items():
                result += f"LHS MID: {lhs_mid.get_string_value()}\n"
                for rhs_mid in rhs_mids:
                    result += f"- RHS MID: {rhs_mid.get_string_value()}\n"
        result += "Reverse links:\n"
        for link_type, links in self._links_reverse.items():
            result += f"Reverse link type: {link_type.name}\n"
            for lhs_mid, rhs_mids in links.items():
                result += f"LHS MID: {lhs_mid.get_string_value()}\n"
                for rhs_mid in rhs_mids:
                    result += f"- RHS MID: {rhs_mid.get_string_value()}\n"
        return result

    def add_node_by_mid(self, mid: MID, uid: Optional[str], node: Any):
        assert isinstance(mid, MID), mid
        assert mid not in self._map_mid_to_node, (self._map_mid_to_node, node)
        self._map_mid_to_node[mid] = node
        if uid is not None:
            self._map_uid_to_node[uid] = node

    def get_node_by_mid(self, mid: MID) -> Any:
        assert isinstance(mid, MID), mid
        if mid not in self._map_mid_to_node:
            raise LookupError
        return self._map_mid_to_node[mid]

    def get_node_by_mid_weak(self, mid: MID) -> Optional[Any]:
        assert isinstance(mid, MID), mid
        if mid not in self._map_mid_to_node:
            return None
        return self._map_mid_to_node[mid]

    def get_node_by_uid(self, uid: str) -> Any:
        assert isinstance(uid, str), uid
        if uid not in self._map_uid_to_node:
            raise LookupError
        return self._map_uid_to_node[uid]

    def get_node_by_uid_weak(self, uid: str) -> Optional[Any]:
        assert isinstance(uid, str), uid
        if uid not in self._map_uid_to_node:
            return None
        return self._map_uid_to_node[uid]

    def remove_node_by_mid(self, mid: MID):
        assert isinstance(mid, MID), mid
        if mid not in self._map_mid_to_node:
            raise LookupError
        if self.remove_node_validation is not None:
            self.remove_node_validation.validate(self, mid)
        node_to_remove = self._map_mid_to_node
        del self._map_mid_to_node[mid]

        uids_to_remove = []
        for uid_, node_ in self._map_uid_to_node.items():
            if node_ == node_to_remove:
                uids_to_remove.append(uid_)
        assert len(uids_to_remove) <= 1
        for uid_to_remove_ in uids_to_remove:
            del self._map_uid_to_node[uid_to_remove_]

    def get_link_values(self, *, link_type: LinkType, lhs_node: Any) -> List:
        if link_type not in self._links:
            raise LookupError
        links: Dict[MID, OrderedSet[MID]] = self._links[link_type]
        if lhs_node.mid not in links:
            raise LookupError
        rhs_mids = self._links[link_type][lhs_node.mid]
        if len(rhs_mids) == 0:
            raise LookupError
        rhs_nodes = []
        for rhs_mid in rhs_mids:
            rhs_nodes.append(self.get_node_by_mid(rhs_mid))
        return rhs_nodes

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
    ) -> Optional[List]:
        if link_type not in self._links:
            return None
        links = self._links[link_type]
        if lhs_node.mid not in links:
            return None
        rhs_nodes = []
        for rhs_mid in links[lhs_node.mid]:
            rhs_nodes.append(self.get_node_by_mid(rhs_mid))
        return rhs_nodes

    def get_link_values_reverse_weak(
        self, *, link_type: LinkType, rhs_node: Any
    ) -> Optional[List]:
        if link_type not in self._links_reverse:
            return None
        reverse_links = self._links_reverse[link_type]
        if rhs_node.mid not in reverse_links:
            return None
        lhs_nodes = []
        for lhs_mid_ in reverse_links[rhs_node.mid]:
            lhs_nodes.append(self.get_node_by_mid(lhs_mid_))
        return lhs_nodes

    def link_exists(self, *, link_type: LinkType, lhs_node: Any) -> bool:
        if link_type not in self._links:
            return False
        links = self._links[link_type]
        if lhs_node.mid not in links:
            return False
        return True

    def node_with_uid_exists(self, *, uid: str) -> bool:
        return uid in self._map_uid_to_node

    def add_link(self, *, link_type: LinkType, lhs_node: Any, rhs_node: Any):
        assert lhs_node != rhs_node, (lhs_node, rhs_node)
        assert lhs_node.mid != rhs_node.mid, (lhs_node, rhs_node)
        assert not isinstance(lhs_node, MID)
        assert not isinstance(rhs_node, MID)
        assert isinstance(lhs_node.mid, MID)
        assert isinstance(rhs_node.mid, MID)

        self._map_mid_to_node[lhs_node.mid] = lhs_node
        self._map_mid_to_node[rhs_node.mid] = rhs_node

        links = self._links[link_type]
        if lhs_node.mid in links:
            assert rhs_node.mid not in links[lhs_node.mid]
        reverse_links = self._links_reverse[link_type]

        if lhs_node.mid not in links:
            links[lhs_node.mid] = OrderedSet([rhs_node.mid])
        else:
            links[lhs_node.mid].add(rhs_node.mid)

        if rhs_node.mid not in reverse_links:
            reverse_links[rhs_node.mid] = OrderedSet([lhs_node.mid])
        else:
            reverse_links[rhs_node.mid].add(lhs_node.mid)

    def remove_link(
        self,
        *,
        link_type: LinkType,
        lhs_node: Any,
        rhs_node: Any,
        remove_lhs_node: bool,
        remove_rhs_node: bool,
    ):
        assert link_type in self._links
        assert isinstance(lhs_node.mid, MID), lhs_node
        assert isinstance(rhs_node.mid, MID), rhs_node
        assert lhs_node.mid in self._links[link_type]
        self._links[link_type][lhs_node.mid].remove(rhs_node.mid)
        self._links_reverse[link_type][rhs_node.mid].remove(lhs_node.mid)
        if remove_lhs_node:
            self.remove_node_by_mid(lhs_node.mid)
        if remove_rhs_node:
            self.remove_node_by_mid(rhs_node.mid)
