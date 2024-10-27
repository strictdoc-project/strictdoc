def hello_world():
    """
    Some text.

    @relation(REQ-1, scope=function)
    """
    # @sdoc[REQ-1]
    print("hello world")  # noqa: T201
    # @sdoc[/REQ-1]
    print("hello world")  # noqa: T201
    # @sdoc[REQ-1]
    print("hello world")  # noqa: T201
    # @sdoc[/REQ-1]
