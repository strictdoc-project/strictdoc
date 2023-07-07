import contextlib


@contextlib.contextmanager
def handle_selenium_exceptions():
    """
    WIP: Catching the Selenium exceptions to understand what to do next
    with regard to #1217:
    "Time to do something with ERR_CONNECTION_REFUSED Selenium errors on CI"
    https://github.com/strictdoc-project/strictdoc/issues/1217
    """
    try:
        yield
    except Exception as exception:
        print(  # noqa: T201
            f"Handling Selenium exception: "
            f"{type(exception).__name__} {exception.args} {exception}"
        )
        raise exception
