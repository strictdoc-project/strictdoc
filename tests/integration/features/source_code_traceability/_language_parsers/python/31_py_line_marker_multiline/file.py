# ruff: noqa

def hello_world():
    # @relation(
    #     REQ-001,
    #     REQ-002,
    #     REQ-003,
    #     scope=line
    # )
    print("Line marker")  # noqa: T201

    # @relation(REQ-001, scope=range_start)
    print("ignored hello world")  # noqa: T201
    print("ignored hello world")  # noqa: T201
    # @relation(REQ-001, scope=range_end)
