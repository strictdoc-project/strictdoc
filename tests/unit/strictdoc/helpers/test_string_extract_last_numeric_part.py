import pytest

from strictdoc.helpers.string import extract_last_numeric_part


def test():
    assert extract_last_numeric_part("0") == "0"
    assert extract_last_numeric_part("REQ-0") == "0"
    assert extract_last_numeric_part("REQ-001") == "001"

    with pytest.raises(ValueError):
        assert extract_last_numeric_part("") is None
    with pytest.raises(ValueError):
        assert extract_last_numeric_part("REQ") is None
