from math import ceil


def round_up(number: float, decimals):
    assert isinstance(number, float)
    assert isinstance(decimals, int)
    assert decimals >= 0
    if decimals == 0:
        return ceil(number)

    factor = 10**decimals

    return ceil(number * factor) / factor
