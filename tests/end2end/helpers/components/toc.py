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
        self.test_case.assert_element(
            '//*[@data-testid="toc-bar"]',
            by=By.XPATH,
        )
        self.test_case.assert_element_present(
            '//*[@data-testid="toc-list"]',
            by=By.XPATH,
        )

    def assert_toc_handler(self) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='toc-handler-button']",
            by=By.XPATH,
        )

    def assert_toc_opened(self) -> None:
        # toc bar has attribute
        self.test_case.assert_element(
            '//*[@data-testid="toc-bar"][@data-state="open"]',
            by=By.XPATH,
        )
        # toc is visible
        self.test_case.assert_element_visible(
            '//*[@data-testid="toc-list"]',
            by=By.XPATH,
        )

    def assert_toc_closed(self) -> None:
        # toc bar has attribute
        self.test_case.assert_element(
            '//*[@data-testid="toc-bar"][@data-state="closed"]',
            by=By.XPATH,
        )
        # toc is hidden
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="toc-list"]',
            by=By.XPATH,
        )

    def do_toggle_toc(self) -> None:
        self.test_case.click_xpath("//*[@data-testid='toc-handler-button']")

    def assert_toc_contains(self, string: str) -> None:
        """The string does not need be visible (TOC may be hidden)."""
        self.test_case.assert_element_present(
            f"//*[@data-testid='toc-list']//*[contains(., '{string}')]",
            by=By.XPATH,
        )

    def assert_toc_contains_not(self, string: str) -> None:
        """The string should not be contained in the TOC (it may be hidden)."""
        self.test_case.assert_element_not_present(
            f"//*[@data-testid='toc-list']//*[contains(., '{string}')]",
            by=By.XPATH,
        )

    # TOC links/anchors

    def do_toc_go_to_anchor(self, anchor) -> None:
        self.test_case.click_xpath(
            f"//*[@data-testid='toc-list']//a[@href='#{anchor}']"
        )

        # check if the link was successfully clicked
        # and that the target is highlighted
        targeted_anchor = f"sdoc-anchor[id='{anchor}']:target"
        self.test_case.assert_element_present(targeted_anchor)
