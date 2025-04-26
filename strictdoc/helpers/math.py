from math import ceil


def round_up(number: float, decimals: int) -> float:
    assert isinstance(number, float)
    assert isinstance(decimals, int)
    assert decimals >= 0

    factor = 10**decimals

    return float(ceil(number * factor) / factor)
