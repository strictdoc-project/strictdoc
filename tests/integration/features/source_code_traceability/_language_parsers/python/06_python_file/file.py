"""
This file does good things.

@relation(REQ-1, scope=file)
"""

class Foo:
    def hello_world(self):
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

def hello_world_2():
    print("hello world")  # noqa: T201
