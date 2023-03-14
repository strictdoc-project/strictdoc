from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class TOC:  # pylint: disable=invalid-name  # noqa: E501
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    def assert_toc_handler(self) -> None:
        self.test_case.assert_element(
            "//*[@id='toc_handler']",
            by=By.XPATH,
        )

    def assert_toc_opened(self, string: str) -> None:
        # body has attribute
        self.test_case.assert_element(
            '//body[@data-toc_state="open"]',
            by=By.XPATH,
        )
        # toc is visible
        self.test_case.assert_element_visible(
            "//*[@id='toc']",
            by=By.XPATH,
        )
        # toc contains test string (if provided)
        if string:
            self.assert_toc_contains_string(string)

    def assert_toc_closed(self) -> None:
        # body has attribute
        self.test_case.assert_element(
            '//body[@data-toc_state="close"]',
            by=By.XPATH,
        )
        # toc is hidden
        self.test_case.assert_element_not_visible(
            "//*[@id='toc']",
            by=By.XPATH,
        )

    def do_toggle_toc(self) -> None:
        self.test_case.click_xpath("//*[@id='toc_handler']")

    # TODO: open/close TOC and state between windows

    def assert_toc_contains_string(self, string: str) -> None:
        self.test_case.assert_element(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]",
            by=By.XPATH,
        )

    def assert_toc_contains_not(self, string: str) -> None:
        self.test_case.assert_element_not_present(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]",
            by=By.XPATH,
        )
