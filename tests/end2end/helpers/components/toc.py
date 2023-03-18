from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class TOC:  # pylint: disable=invalid-name  # noqa: E501
    """Table of contents"""

    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    def assert_is_toc(self) -> None:
        self.assert_toc_handler()
        self.assert_toc_panel()

    def assert_toc_panel(self) -> None:
        self.test_case.assert_element_present(
            "//*[@id='toc']",
            by=By.XPATH,
        )

    def assert_toc_handler(self) -> None:
        self.test_case.assert_element(
            "//*[@id='toc_handler']",
            by=By.XPATH,
        )

    def assert_toc_opened(self) -> None:
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

    def assert_toc_contains(self, string: str) -> None:
        """The string does not need be visible (TOC may be hidden)."""
        self.test_case.assert_element_present(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]",
            by=By.XPATH,
        )

    def assert_toc_contains_not(self, string: str) -> None:
        """The string should not be contained in the TOC (it may be hidden)."""
        self.test_case.assert_element_not_present(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]",
            by=By.XPATH,
        )
