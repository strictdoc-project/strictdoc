#!/usr/bin/python
"""
@relation(REQ-001, scope=file)
"""

def hello_world():
    # @relation(REQ-001, scope=range_start)
    print("ignored hello world")  # noqa: T201
    print("ignored hello world")  # noqa: T201
    # @relation(REQ-001, scope=range_end)
