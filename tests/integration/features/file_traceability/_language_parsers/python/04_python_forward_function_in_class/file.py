class Foo:
    def hello_world(self):
        """
        @relation(REQ-1, scope=function)
        """
        # @relation(REQ-1, scope=range_start)
        print("hello world")  # noqa: T201
        # @relation(REQ-1, scope=line)
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        # @relation(REQ-1, scope=range_end)

def hello_world_2():
    print("hello world")  # noqa: T201
