
class Foo:

    def hello_world(self):
        """
        @relation(REQ-1, scope=function)
        """
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

        def nested_function():
            """
            @relation(REQ-2, scope=function)
            """
            print("hello world")  # noqa: T201

        nested_function()

def hello_world_2():
        """
        @relation(REQ-3, scope=function)
        """
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

        def nested_function():
            """
            @relation(REQ-4, scope=function)
            """
            print("hello world")  # noqa: T201

        nested_function()

class Outer:
    class Inner:
        def hello_world(self):
            """
            @relation(REQ-5, scope=function)
            """
            print("hello world")  # noqa: T201
