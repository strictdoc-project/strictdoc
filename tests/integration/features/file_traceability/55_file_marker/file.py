"""
@relation(REQ-001, scope=file)
"""

def hello_world():
    # @sdoc[REQ-001]
    print("ignored hello world")  # noqa: T201
    print("ignored hello world")  # noqa: T201
    # @sdoc[/REQ-001]
