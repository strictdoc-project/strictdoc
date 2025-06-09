from strictdoc.core.graph.one_to_one_dictionary import OneToOneDictionary


def test_01_basic():
    container = OneToOneDictionary(int, int)

    container.create_link(lhs_node=5, rhs_node=3)

    assert container.get_link_value(lhs_node=5) == 3
    assert container.get_count() == 1

    container.delete_link(lhs_node=5, rhs_node=3)

    assert container.get_count() == 0
