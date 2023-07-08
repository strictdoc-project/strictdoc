from strictdoc.helpers.mid import MID


def test_unique_mid():
    mid1 = MID.create()
    mid2 = MID(mid1.mid)

    assert hash(mid1) == hash(mid2)


def test_dict():
    mid1 = MID.create()
    store = {mid1: True}

    mid2 = MID(mid1.mid)
    assert store[mid2] is True
