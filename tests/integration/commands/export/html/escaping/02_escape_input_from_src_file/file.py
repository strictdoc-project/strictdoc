# <b>"escaping"&nbsp;'line mark'</b> @sdoc(REQ-1)
def print_test():
    test1 = """
    <b>"escaping"&nbsp;'normal src line'</b>
    """
    test2 = """<b>"escaping"&nbsp;'forward range mark before'</b>
    <b>"escaping"&nbsp;'forward range mark after'</b>
    """
    print(f"{test1} {test2}")  # noqa: T201#


# <b>"escaping"&nbsp;'range mark before'</b> @sdoc[REQ-1]
def hello_world():
    print("hello world")  # noqa: T201
# <b>"escaping"&nbsp;'range mark after'</b> @sdoc[/REQ-1]
