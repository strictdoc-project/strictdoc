from enum import IntEnum

import pytest

from strictdoc.core.graph_database import (
    GraphDatabase,
    LinkType,
)
from strictdoc.helpers.mid import MID

NOT_RELEVANT = "NOT_RELEVANT"


def test_01():
    graph_database = GraphDatabase()

    mid: MID = MID.create()
    node = 1

    graph_database.add_node(mid=mid, node=node)
    assert graph_database.get_node(mid) == 1

    graph_database.remove_node(mid=mid)

    with pytest.raises(LookupError):
        graph_database.get_node(mid=mid)


def test_02():
    class Relation(LinkType, IntEnum):
        INLINE_LINK_TO_ANCHOR = 1

    anchor = "anchor"
    anchor_mid = MID.create()
    inline_link = "inline_link"
    inline_link_mid = MID.create()

    graph_database = GraphDatabase()
    graph_database.add_node(anchor_mid, anchor)
    graph_database.add_node(inline_link_mid, inline_link)

    graph_database.add_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link_mid,
        rhs_node=anchor_mid,
    )
    graph_database.remove_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link_mid,
        rhs_node=anchor_mid,
    )
    graph_database.remove_node(anchor_mid)
