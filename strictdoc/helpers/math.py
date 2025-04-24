# mypy: disable-error-code="no-untyped-def"
from math import ceil


def round_up(number: float, decimals):
    assert isinstance(number, float)
    assert isinstance(decimals, int)
    assert decimals >= 0

    factor = 10**decimals

    return ceil(number * factor) / factor
