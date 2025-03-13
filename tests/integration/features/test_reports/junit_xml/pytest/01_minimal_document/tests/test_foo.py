from src.foo import foo


def test_foo():
    """
    @relation(REQ-1, scope=function)
    """
    assert foo()
