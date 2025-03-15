# ruff: noqa
import pytest


@pytest.mark.skip(reason="This test is skipped for now.")
def test_foo():
    """
    @relation(REQ-1, scope=function)
    """
    assert False
