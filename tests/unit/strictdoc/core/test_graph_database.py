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

    graph_database.add_node_by_mid(mid=mid, uid=None, node=node)
    assert graph_database.get_node_by_mid(mid) == 1

    graph_database.remove_node_by_mid(mid=mid)

    with pytest.raises(LookupError):
        graph_database.get_node_by_mid(mid=mid)


def test_02():
    class Relation(LinkType):
        INLINE_LINK_TO_ANCHOR = 1

    class Node:
        def __init__(self, title):
            self.title = title
            self.reserved_mid = MID.create()

    anchor = Node("anchor")
    inline_link = Node("inline_link")

    graph_database = GraphDatabase()
    graph_database.add_node_by_mid(anchor.reserved_mid, None, anchor)
    graph_database.add_node_by_mid(inline_link.reserved_mid, None, inline_link)

    graph_database.add_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link,
        rhs_node=anchor,
    )
    graph_database.remove_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link,
        rhs_node=anchor,
        remove_lhs_node=False,
        remove_rhs_node=False,
    )
    graph_database.remove_node_by_mid(anchor.reserved_mid)
