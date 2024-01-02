from strictdoc.core.graph.many_to_many_set import ManyToManySet
from strictdoc.core.graph.one_to_one_dictionary import OneToOneDictionary
from strictdoc.core.graph_database import (
    GraphDatabase,
)


def test_01_basic():
    class Relation:
        INLINE_LINK_TO_ANCHOR = 1

    class Node:
        def __init__(self, title):
            self.title = title

    anchor = Node("anchor")
    inline_link = Node("inline_link")

    graph_database = GraphDatabase(
        buckets=[
            (Relation.INLINE_LINK_TO_ANCHOR, OneToOneDictionary(Node, Node))
        ]
    )

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
    class Relation:
        INLINE_LINK_TO_ANCHOR = 1

    class Node:
        def __init__(self, title):
            self.title = title

    anchor = Node("anchor")
    inline_link = Node("inline_link")

    graph_database = GraphDatabase(
        buckets=[(Relation.INLINE_LINK_TO_ANCHOR, ManyToManySet(Node, Node))]
    )

    graph_database.create_link(
        link_type=Relation.INLINE_LINK_TO_ANCHOR,
        lhs_node=anchor,
        rhs_node=inline_link,
    )
    assert graph_database.get_link_values_reverse(
        link_type=Relation.INLINE_LINK_TO_ANCHOR, rhs_node=inline_link
    ) == {anchor}
