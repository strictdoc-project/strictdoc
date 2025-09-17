def hello_world():
    # @relation(REQ-001, scope=line)
    print("Line marker")  # noqa: T201

    # @sdoc[REQ-001]
    print("ignored hello world")  # noqa: T201
    print("ignored hello world")  # noqa: T201
    # @sdoc[/REQ-001]
