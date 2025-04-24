from strictdoc.helpers.math import round_up


def test_round_up():
    assert round_up(1.3333, 0) == 2
    assert round_up(1.3333, 1) == 1.4
    assert round_up(1.3333, 2) == 1.34
    assert round_up(1.3333, 3) == 1.334
    assert round_up(1.3333, 4) == 1.3333
    assert round_up(1.3333, 5) == 1.3333
