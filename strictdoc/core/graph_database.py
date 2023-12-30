from collections import defaultdict
from enum import Enum
from typing import Any, Dict, Optional

from strictdoc.helpers.mid import MID
from strictdoc.helpers.ordered_set import OrderedSet


class ConstraintViolation(Exception):
    def __init__(self, message):
        super().__init__(message)


class LinkType(Enum):
    def __init__(self, rank, relation_type, lhs_type, rhs_type):
        assert relation_type in ("ONE_TO_ONE", "ONE_TO_MANY")
        self.rank = rank
        self.relation_type: str = relation_type
        self.lhs_type = lhs_type
        self.rhs_type = rhs_type

    def is_one_to_one(self):
        return self.relation_type == "ONE_TO_ONE"


class GraphDatabase:
    def __init__(self):
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
                result += f"LHS MID: {lhs_mid}\n"
                for rhs_mid in rhs_mids:
                    result += f"- RHS MID: {rhs_mid}\n"
        result += "Reverse links:\n"
        for link_type, links in self._links_reverse.items():
            result += f"Reverse link type: {link_type.name}\n"
            for lhs_mid, rhs_mids in links.items():
                result += f"LHS MID: {lhs_mid}\n"
                for rhs_mid in rhs_mids:
                    result += f"- RHS MID: {rhs_mid}\n"
        return result

    def has_link(self, *, link_type: LinkType, lhs_node: Any) -> bool:
        if link_type not in self._links:
            return False
        links = self._links[link_type]
        if lhs_node not in links:
            return False
        return True

    def get_link_value(
        self, *, link_type: LinkType, lhs_node: Any, weak: bool
    ) -> Optional[Any]:
        link_values = self.get_link_values(
            link_type=link_type, lhs_node=lhs_node, weak=True
        )
        if link_values is not None and len(link_values) > 0:
            assert len(link_values) == 1
            return next(iter(link_values))
        if weak:
            return None
        raise LookupError

    def get_link_values(
        self, *, link_type: LinkType, lhs_node: Any, weak: bool
    ) -> Optional[OrderedSet]:
        if link_type not in self._links:
            if weak:
                return None
            raise LookupError
        links = self._links[link_type]
        if lhs_node not in links:
            return None
        return links[lhs_node]

    def get_link_values_reverse(
        self, *, link_type: LinkType, rhs_node: Any, weak: bool
    ) -> Optional[OrderedSet]:
        if link_type not in self._links_reverse:
            if weak:
                return None
            raise LookupError
        reverse_links = self._links_reverse[link_type]
        if rhs_node not in reverse_links:
            if weak:
                return None
            raise LookupError
        return reverse_links[rhs_node]

    def create_link(self, *, link_type: LinkType, lhs_node: Any, rhs_node: Any):
        if not isinstance(lhs_node, link_type.lhs_type):
            raise TypeError(
                f"Type mismatch: {type(lhs_node)} {link_type.lhs_type}"
            )

        assert lhs_node != rhs_node, (lhs_node, rhs_node)

        links = self._links[link_type]
        reverse_links = self._links_reverse[link_type]

        if lhs_node not in links:
            links[lhs_node] = OrderedSet([rhs_node])
        else:
            if link_type.is_one_to_one():
                raise TypeError(
                    "The LHS node already exists for this one-to-one relation. "
                    "Cannot insert another one. "
                    f"Link type: {link_type}, "
                    f"LHS node: {lhs_node}, "
                    f"RHS node: {rhs_node}."
                )
            links[lhs_node].add(rhs_node)

        if rhs_node not in reverse_links:
            reverse_links[rhs_node] = OrderedSet([lhs_node])
        else:
            reverse_links[rhs_node].add(lhs_node)

    def delete_link(
        self,
        *,
        link_type: LinkType,
        lhs_node: Any,
        rhs_node: Any,
    ):
        assert link_type in self._links
        assert lhs_node in self._links[link_type]
        if self.remove_node_validation is not None:
            self.remove_node_validation.validate(self, link_type, lhs_node)

        self._links[link_type][lhs_node].remove(rhs_node)
        self._links_reverse[link_type][rhs_node].remove(lhs_node)

    def delete_all_links(
        self,
        *,
        link_type: LinkType,
        lhs_node: Any,
    ):
        assert link_type in self._links
        assert lhs_node in self._links[link_type]
        if self.remove_node_validation is not None:
            self.remove_node_validation.validate(self, link_type, lhs_node)

        existing_rhs_nodes = self._links[link_type][lhs_node]
        for existing_rhs_node_ in existing_rhs_nodes:
            self._links_reverse[link_type][existing_rhs_node_].remove(lhs_node)

        del self._links[link_type][lhs_node]
