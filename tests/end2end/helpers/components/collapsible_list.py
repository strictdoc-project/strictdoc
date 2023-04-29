from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class CollapsibleList:
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    def assert_is_collapsible(self) -> None:
        self.assert_collapsible_list()
        self.assert_collapsible_handler()

    # assert elements

    def assert_collapsible_list(self) -> None:
        self.test_case.assert_element(
            "//*[@js-collapsible_list]",
            by=By.XPATH,
        )

    def assert_collapsible_handler(self) -> None:
        self.test_case.assert_element(
            "//*[@data-collapsible_list__branch]",
            by=By.XPATH,
        )

    # assert global list state

    def assert_all_is_expanded(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-collapsible_list__branch="closed"]',
            by=By.XPATH,
        )

    def assert_all_is_collapsed(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-collapsible_list__branch="open"]',
            by=By.XPATH,
        )

    # assert single item state

    def assert_is_expanded(self, string: str) -> None:
        self.test_case.assert_element(
            f'//a[contains(., "{string}")]/..'
            '/*[@data-collapsible_list__branch="open"]',
            by=By.XPATH,
        )

    def assert_is_collapsed(self, string: str) -> None:
        self.test_case.assert_element(
            f'//a[contains(., "{string}")]/..'
            '/*[@data-collapsible_list__branch="closed"]',
            by=By.XPATH,
        )

    # assert list contains

    def assert_visible(self, string: str) -> None:
        self.test_case.assert_element(
            f'//*[@js-collapsible_list]//a[contains(., "{string}")]',
            by=By.XPATH,
        )

    def assert_visible_not(self, string: str) -> None:
        self.test_case.assert_element_not_visible(
            f'//*[@js-collapsible_list]//a[contains(., "{string}")]',
            by=By.XPATH,
        )

    # do

    def do_toggle_collapsible(self, string: str) -> None:
        self.test_case.click_xpath(
            f'//a[contains(., "{string}")]/..'
            "/*[@data-collapsible_list__branch]",
        )

    def do_bulk_collapse(self, string: str) -> None:
        self.test_case.double_click(
            f'//a[contains(., "{string}")]/..'
            '/*[@data-collapsible_list__branch="open"]',
            by=By.XPATH,
        )

    def do_bulk_expand(self, string: str) -> None:
        self.test_case.double_click(
            f'//a[contains(., "{string}")]/..'
            '/*[@data-collapsible_list__branch="closed"]',
            by=By.XPATH,
        )
