class Foo:
    """
    @relation(REQ-1, scope=class)
    """

    def hello_world(self):
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

def hello_world_2():
    print("hello world")  # noqa: T201
