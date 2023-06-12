from enum import IntEnum

import pytest

from strictdoc.core.graph_database import (
    UUID,
    GraphDatabase,
    LinkType,
)

NOT_RELEVANT = "NOT_RELEVANT"


def test_01():
    graph_database = GraphDatabase()

    uuid: UUID = UUID.create()
    node = 1

    graph_database.add_node(uuid=uuid, node=node)
    assert graph_database.get_node(uuid) == 1

    graph_database.remove_node(uuid=uuid)

    with pytest.raises(LookupError):
        graph_database.get_node(uuid=uuid)


def test_02():
    class Relation(LinkType, IntEnum):
        INLINE_LINK_TO_ANCHOR = 1

    anchor = "anchor"
    anchor_uuid = UUID.create()
    inline_link = "inline_link"
    inline_link_uuid = UUID.create()

    graph_database = GraphDatabase()
    graph_database.add_node(anchor_uuid, anchor)
    graph_database.add_node(inline_link_uuid, inline_link)

    graph_database.add_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link_uuid,
        rhs_node=anchor_uuid,
    )
    graph_database.remove_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link_uuid,
        rhs_node=anchor_uuid,
    )
    graph_database.remove_node(anchor_uuid)
