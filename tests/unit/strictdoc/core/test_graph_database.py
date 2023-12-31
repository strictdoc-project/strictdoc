import pytest

from strictdoc.core.graph_database import (
    GraphDatabase,
    LinkType,
)


def test_01_basic():
    class Node:
        def __init__(self, title):
            self.title = title

    class Relation(LinkType):
        INLINE_LINK_TO_ANCHOR = (1, "ONE_TO_ONE", Node, Node)

    anchor = Node("anchor")
    inline_link = Node("inline_link")

    graph_database = GraphDatabase()

    graph_database.create_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link,
        rhs_node=anchor,
    )
    assert (
        graph_database.get_link_value(
            link_type=Relation.INLINE_LINK_TO_ANCHOR,
            lhs_node=inline_link,
        )
        == anchor
    )
    assert list(
        graph_database.get_link_values(
            link_type=Relation.INLINE_LINK_TO_ANCHOR,
            lhs_node=inline_link,
        )
    ) == [anchor]
    assert list(
        graph_database.get_link_values_reverse(
            link_type=Relation.INLINE_LINK_TO_ANCHOR,
            rhs_node=anchor,
        )
    ) == [inline_link]
    graph_database.delete_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=inline_link,
        rhs_node=anchor,
    )

    assert (
        graph_database.get_link_value_weak(
            link_type=Relation.INLINE_LINK_TO_ANCHOR,
            lhs_node=inline_link,
        )
        is None
    )


def test_02_basic():
    class Relation(LinkType):
        INLINE_LINK_TO_ANCHOR = (1, "ONE_TO_ONE", int, int)

    graph_database = GraphDatabase()

    with pytest.raises(TypeError):
        graph_database.create_link(
            link_type=Relation.INLINE_LINK_TO_ANCHOR,
            lhs_node="foo",
            rhs_node="bar",
        )
