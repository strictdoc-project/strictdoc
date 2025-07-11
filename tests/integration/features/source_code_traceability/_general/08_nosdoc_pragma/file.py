def hello_world():
    # @sdoc[nosdoc]
    # @sdoc[REQ-001]
    print("ignored hello world")  # noqa: T201
    # @sdoc[/REQ-001]
    # @sdoc[/nosdoc]
    # @sdoc[REQ-001]
    print("real hello world")  # noqa: T201
    # @sdoc[/REQ-001]
