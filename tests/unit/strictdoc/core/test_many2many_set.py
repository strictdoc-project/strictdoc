import pytest

from strictdoc.core.graph.many_to_many_set import ManyToManySet


def test_01_basic():
    many2many_set = ManyToManySet(int, int)

    assert many2many_set.get_link_values_weak(lhs_node=1) is None
    with pytest.raises(KeyError):
        many2many_set.get_link_values(lhs_node=1)

    many2many_set.create_link(lhs_node=1, rhs_node=2)
    many2many_set.create_link(lhs_node=1, rhs_node=3)
    many2many_set.create_link(lhs_node=1, rhs_node=4)

    assert many2many_set.get_link_values_weak(lhs_node=1) == {2, 3, 4}
    assert many2many_set.get_link_values(lhs_node=1) == {2, 3, 4}
    assert many2many_set.get_link_values_reverse_weak(rhs_node=2) == {1}
    assert many2many_set.get_link_values_reverse_weak(rhs_node=3) == {1}
    assert many2many_set.get_link_values_reverse_weak(rhs_node=4) == {1}

    many2many_set.delete_link(lhs_node=1, rhs_node=4)
    assert many2many_set.get_link_values_weak(lhs_node=1) == {2, 3}
    assert many2many_set.get_link_values(lhs_node=1) == {2, 3}
    assert many2many_set.get_link_values_reverse_weak(rhs_node=2) == {1}
    assert many2many_set.get_link_values_reverse_weak(rhs_node=3) == {1}
    assert many2many_set.get_link_values_reverse_weak(rhs_node=4) is None

    with pytest.raises(KeyError):
        assert many2many_set.get_link_values_reverse(rhs_node=4)

    many2many_set.delete_all_links(lhs_node=1)
    assert many2many_set.get_link_values_weak(lhs_node=1) is None
    assert many2many_set.get_link_values_reverse_weak(rhs_node=2) is None
    assert many2many_set.get_link_values_reverse_weak(rhs_node=3) is None
    assert many2many_set.get_link_values_reverse_weak(rhs_node=4) is None


def test_02_basic():
    many2many_set = ManyToManySet(int, int)
    many2many_set.delete_link_weak(lhs_node=1, rhs_node=2)

    many2many_set.create_link(lhs_node=1, rhs_node=2)
    assert many2many_set.get_link_values(lhs_node=1) == {2}

    many2many_set.delete_link_weak(lhs_node=1, rhs_node=2)
    assert many2many_set.get_link_values_weak(lhs_node=1) is None


def test_03_basic():
    many2many_set = ManyToManySet(int, int)

    with pytest.raises(TypeError):
        many2many_set.create_link(lhs_node="WRONG", rhs_node=2)
