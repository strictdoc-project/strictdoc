# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import Any

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.core.graph_database import (
    ConstraintViolation,
    GraphDatabase,
)
from strictdoc.core.traceability_index import GraphLinkType
from strictdoc.helpers.mid import MID


class RemoveNodeValidation:
    """
    FIXME: This class is not tested. Also, most of the code should rather be
           in the "can perform operation?"-kind of class.
    """

    def validate(
        self, database: GraphDatabase, link_type: GraphLinkType, lhs_node: Any
    ):
        if link_type == GraphLinkType.MID_TO_NODE:
            assert isinstance(lhs_node, MID)
            node = database.get_link_value(
                link_type=GraphLinkType.MID_TO_NODE,
                lhs_node=lhs_node,
            )
            if isinstance(node, Anchor):
                self.validate_anchor(database, node)

    @staticmethod
    def validate_anchor(database: GraphDatabase, anchor: Anchor):
        assert isinstance(anchor, Anchor)

        existing_links = database.get_link_values_weak(
            link_type=GraphLinkType.NODE_TO_INCOMING_LINKS,
            lhs_node=anchor.reserved_mid,
        )

        if existing_links is not None:
            raise ConstraintViolation(
                f"Cannot delete anchor {anchor} because it has incoming links: "
                f"{anchor.value} -> {existing_links}"
            )
