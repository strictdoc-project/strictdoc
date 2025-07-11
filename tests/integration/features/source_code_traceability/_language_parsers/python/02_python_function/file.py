def hello_world():
    """
    Some text.

    @relation(REQ-1, scope=function)
    """
    # @relation(REQ-1, scope=range_start)
    print("hello world")  # noqa: T201
    # @relation(REQ-1, scope=range_end)
    print("hello world")  # noqa: T201
    # @relation(REQ-1, scope=range_start)
    print("hello world")  # noqa: T201
    # @relation(REQ-1, scope=range_end)

def non_covered_function():
    pass
