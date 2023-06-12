from collections import OrderedDict

import pytest

from strictdoc.helpers.cast import assert_cast


def test_assert_cast():
    assert_cast(1, int)
    assert_cast(OrderedDict(), (dict, OrderedDict))
    assert_cast(OrderedDict(), (list, OrderedDict))
    with pytest.raises(AssertionError):
        assert_cast(OrderedDict(), (list, list))
