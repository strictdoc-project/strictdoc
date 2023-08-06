from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.core.graph_database import (
    ConstraintViolation,
    GraphDatabase,
)
from strictdoc.core.traceability_index import GraphLinkType
from strictdoc.helpers.mid import MID


class RemoveNodeValidation:
    def validate(self, database: GraphDatabase, uuid: MID):
        node = database.get_node_by_mid(uuid)
        if isinstance(node, Anchor):
            self.validate_anchor(database, node)

    @staticmethod
    def validate_anchor(database: GraphDatabase, anchor: Anchor):
        assert isinstance(anchor, Anchor)

        existing_link = database.get_link_value_weak(
            link_type=GraphLinkType.SECTIONS_TO_INCOMING_LINKS,
            lhs_node=anchor.value,
        )

        if existing_link is not None:
            raise ConstraintViolation(
                f"Cannot delete anchor {anchor} because it has incoming links: "
                f"{anchor.value} -> {existing_link}"
            )
