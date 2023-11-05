from time import sleep

from selenium.common import WebDriverException
from seleniumbase import BaseCase


def selenium_connection_error_retry_handler(times):
    """
    Catching the Selenium exceptions to fix a sporadic ERR_CONNECTION_REFUSED
    Selenium error.

    The issue #1217:
    "Time to do something with ERR_CONNECTION_REFUSED Selenium errors on CI"
    https://github.com/strictdoc-project/strictdoc/issues/1217
    """

    def decorator(func):
        def newfn(*args, **kwargs):
            final_exception = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except WebDriverException as exception:
                    print(  # noqa: T201
                        "selenium_connection_error_try_handler: "
                        f"Exception {type(exception)} thrown when attempting "
                        f"to run {func}, "
                        f"attempt {attempt} of {times}."
                    )
                    final_exception = exception

                    # If this is the notorious ERR_CONNECTION_REFUSED exception,
                    # we try again.
                    if "ERR_CONNECTION_REFUSED" in exception.msg:
                        print(  # noqa: T201
                            "selenium_connection_error_try_handler: "
                            "This is a ERR_CONNECTION_REFUSED exception. "
                            "Trying again..."
                        )
                        sleep(0.5)
                        continue

                    # If this is anything but ERR_CONNECTION_REFUSED exception,
                    # we raise right away.
                    break
            raise final_exception

        return newfn

    return decorator


class E2ECase(BaseCase):
    @selenium_connection_error_retry_handler(3)
    def open(self, url):  # noqa: A003
        super().open(url)

    @selenium_connection_error_retry_handler(3)
    def assert_element(self, selector, by="css selector", timeout=None):
        super().assert_element(selector, by, timeout)

    def paste_text(self) -> str:
        self.driver.set_permissions("clipboard-read", "granted")
        pasted_text = self.execute_script(
            "const text = await navigator.clipboard.readText(); return text;"
        )
        return pasted_text
