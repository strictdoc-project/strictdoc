#
# Some No-Op Decorators.
#
def decorator_1(func):
    return func

def decorator_2(func):
    return func

def decorator_3(func):
    return func

def decorator_4(func):
    return func

class Foo:

    def hello_world(self):
        """
        @relation(REQ-1, scope=function)
        """
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

    @decorator_1
    def hello_world_decorated_once(self):
        """
        @relation(REQ-2, scope=function)
        """
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

    @decorator_1
    @decorator_2
    def hello_world_decorated_twice(self):
        """
        @relation(REQ-3, scope=function)
        """
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

    @decorator_1
    @decorator_2
    @decorator_3
    def hello_world_decorated_three_times(self):
        """
        @relation(REQ-4, scope=function)
        """
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

    @decorator_1
    @decorator_2
    @decorator_3
    @decorator_4
    def hello_world_decorated_four_times(self):
        """
        @relation(REQ-5, scope=function)
        """
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201
        print("hello world")  # noqa: T201

