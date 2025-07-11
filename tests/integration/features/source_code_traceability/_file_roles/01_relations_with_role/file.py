class Foo:
    """@relation(REQ-001, scope=class, role=Implementation)"""

    pass


def foo():
    """@relation(REQ-001, scope=function, role=Implementation)"""

    pass


# @relation(REQ-001, scope=range_start, role=Implementation)
def bar1():
    pass


def bar2():
    pass
# @relation(REQ-001, scope=range_end)


if __name__ == "__main__":
    pass  # @relation(REQ-001, scope=line, role=Implementation)
