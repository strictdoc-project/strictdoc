def hello_world():
    # @relation(skip, scope=range_start)
    # @relation(REQ-001, scope=range_start)
    print("ignored hello world")  # noqa: T201
    # @relation(REQ-001, scope=range_end)
    # @relation(skip, scope=range_end)
    # @relation(REQ-001, scope=range_start)
    print("real hello world")  # noqa: T201
    # @relation(REQ-001, scope=range_end)
