def hello_world():
    """
    @relation(REQ-1, scope=function)
    """
    # @sdoc[REQ-1]
    print("hello world")  # noqa: T201
    # @sdoc(REQ-1)
    print("hello world")  # noqa: T201
    print("hello world")  # noqa: T201
    # @sdoc[/REQ-1]

def hello_world_2():
    print("hello world")  # noqa: T201
