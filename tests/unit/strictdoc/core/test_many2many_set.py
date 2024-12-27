import pytest

from strictdoc.core.graph.abstract_bucket import ALL_EDGES
from strictdoc.core.graph.many_to_many_set import ManyToManySet
from strictdoc.helpers.ordered_set import OrderedSet


def test_01_basic():
    many2many_set = ManyToManySet(int, int)

    assert many2many_set.get_link_values(lhs_node=1) == OrderedSet()

    many2many_set.create_link(lhs_node=1, rhs_node=2)
    many2many_set.create_link(lhs_node=1, rhs_node=3)
    many2many_set.create_link(lhs_node=1, rhs_node=4)

    assert many2many_set.get_link_values(lhs_node=1) == {2, 3, 4}
    assert many2many_set.get_link_values_reverse(rhs_node=2) == {1}

    many2many_set.delete_link(lhs_node=1, rhs_node=4)
    assert many2many_set.get_link_values(lhs_node=1) == {2, 3}
    assert many2many_set.get_link_values_reverse(rhs_node=2) == {1}
    assert many2many_set.get_link_values_reverse(rhs_node=3) == {1}
    assert many2many_set.get_link_values_reverse(rhs_node=4) == OrderedSet()

    many2many_set.delete_all_links(lhs_node=1)
    assert many2many_set.get_link_values(lhs_node=1) == OrderedSet()
    assert many2many_set.get_link_values_reverse(rhs_node=2) == OrderedSet()
    assert many2many_set.get_link_values_reverse(rhs_node=3) == OrderedSet()
    assert many2many_set.get_link_values_reverse(rhs_node=4) == OrderedSet()


def test_02_basic():
    many2many_set = ManyToManySet(int, int)
    many2many_set.delete_link_weak(lhs_node=1, rhs_node=2)

    many2many_set.create_link(lhs_node=1, rhs_node=2)
    assert many2many_set.get_link_values(lhs_node=1) == {2}

    many2many_set.delete_link_weak(lhs_node=1, rhs_node=2)
    assert many2many_set.get_link_values(lhs_node=1) == OrderedSet()


def test_03_basic():
    many2many_set = ManyToManySet(int, int)

    with pytest.raises(TypeError):
        many2many_set.create_link(lhs_node="WRONG", rhs_node=2)


def test_10_edges():
    many2many_set = ManyToManySet(int, int)

    many2many_set.create_link(lhs_node=1, rhs_node=2, edge="refines")
    assert many2many_set.get_link_values(lhs_node=1, edge="refines") == {2}

    many2many_set.delete_link_weak(lhs_node=1, rhs_node=2, edge="refines")
    assert (
        many2many_set.get_link_values(lhs_node=1, edge="refines")
        == OrderedSet()
    )


def test_12_working_with_all_edges():
    many2many_set = ManyToManySet(int, int)

    assert many2many_set.get_count(edge="refines") == 0
    assert many2many_set.get_count(edge="verifies") == 0
    assert many2many_set.get_count(edge=ALL_EDGES) == 0

    many2many_set.create_link(lhs_node=1, rhs_node=2, edge="refines")
    many2many_set.create_link(lhs_node=1, rhs_node=2, edge="verifies")
    many2many_set.create_link(lhs_node=1, rhs_node=3, edge="verifies")

    assert many2many_set.get_count(edge="refines") == 1
    assert many2many_set.get_count(edge="verifies") == 2
    assert many2many_set.get_count(edge=ALL_EDGES) == 3

    assert many2many_set.get_link_values(lhs_node=1, edge="refines") == {2}
    assert many2many_set.get_link_values(lhs_node=1, edge="verifies") == {2, 3}
    assert many2many_set.get_link_values(lhs_node=1, edge=ALL_EDGES) == {2, 3}

    many2many_set.delete_link(lhs_node=1, rhs_node=2, edge=ALL_EDGES)

    assert many2many_set.get_count(edge="refines") == 0
    assert many2many_set.get_count(edge="verifies") == 1
    assert many2many_set.get_count(edge=ALL_EDGES) == 1

    many2many_set.delete_link(lhs_node=1, rhs_node=3, edge=ALL_EDGES)
    assert many2many_set.get_count(edge="refines") == 0
    assert many2many_set.get_count(edge="verifies") == 0
    assert many2many_set.get_count(edge=ALL_EDGES) == 0
