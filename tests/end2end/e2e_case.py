"""
@relation(SDOC-SRS-46, scope=file)
"""

from time import sleep
from urllib.parse import urlparse, urlunparse

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
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

    def do_paste_text_via_js(self, element, text: str) -> None:
        # Simulates a paste event on a DOM element with arbitrary text content.
        # Cross-platform clipboard access is unreliable in headless Selenium.
        self.execute_script(
            """
            const el = arguments[0];
            el.focus();
            const range = document.createRange();
            range.selectNodeContents(el);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
            const dt = new DataTransfer();
            dt.setData('text/plain', arguments[1]);
            el.dispatchEvent(new ClipboardEvent('paste', {
                bubbles: true,
                cancelable: true,
                clipboardData: dt
            }));
            """,
            element,
            text,
        )

    def paste_text(self) -> str:
        self.driver.set_permissions("clipboard-read", "granted")
        pasted_text = self.execute_script(
            "const text = await navigator.clipboard.readText(); return text;"
        )
        return pasted_text

    def assert_url_not_contains(self, substring: str) -> None:
        current_url = self.get_current_url()
        assert substring not in current_url, (
            f"Expected URL to not contain {substring!r}, but got: {current_url}"
        )

    def clear_local_storage(self) -> None:
        self.execute_script("localStorage.clear()")

    def reload_page_without_query(self) -> None:
        parsed = urlparse(self.get_current_url())
        clean_url = urlunparse(parsed._replace(query="", fragment=""))
        self.open(clean_url)

    def sdoc_do_scroll_to_element_by_xpath(self, xpath: str) -> None:
        assert isinstance(xpath, str), xpath
        element = self.wait_for_element_visible(
            xpath,
            by=By.XPATH,
        )
        self.execute_script(
            "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
            element,
        )
