from strictdoc.helpers.mid import MID


def test_mid_instance():
    mid1 = MID.create()

    assert isinstance(mid1, MID)
    assert isinstance(mid1, str)


def test_unique_mid():
    mid1 = MID.create()
    mid2 = MID(mid1)

    assert hash(mid1) == hash(mid2)


def test_dict():
    mid1 = MID.create()
    store = {mid1: True}

    mid2 = MID(mid1)
    assert store[mid2] is True
