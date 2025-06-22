from strictdoc.helpers.ordered_set import OrderedSet


def test_basic():
    ordered_set = OrderedSet()

    ordered_set.add(1)
    ordered_set.add(2)
    ordered_set.add(3)

    assert len(ordered_set) == 3
    assert ordered_set.__getitem__(0) == 1
    assert ordered_set.__getitem__(2) == 3

    assert str(ordered_set) == "{1, 2, 3}"
    assert repr(ordered_set) == "<OrderedSet {1, 2, 3}>"

    ordered_set.clear()
    assert len(ordered_set) == 0
