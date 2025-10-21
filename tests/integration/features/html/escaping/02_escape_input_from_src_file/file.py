# <b>"escaping"&nbsp;'line mark'</b> @relation(REQ-1, scope=line)
def print_test():
    test1 = """
    <b>"escaping"&nbsp;'normal src line'</b>
    """
    test2 = """<b>"escaping"&nbsp;'forward range mark before'</b>
    <b>"escaping"&nbsp;'forward range mark after'</b>
    """
    print(f"{test1} {test2}")  # noqa: T201#


# <b>"escaping"&nbsp;'range mark before'</b> @relation(REQ-1, scope=range_start)
def hello_world():
    print("hello world")  # noqa: T201
# <b>"escaping"&nbsp;'range mark after'</b> @relation(REQ-1, scope=range_end)
