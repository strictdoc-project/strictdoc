from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
            "//*[@data-handler]",
            by=By.XPATH,
        )

    def assert_bulk_panel(self) -> None:
        self.test_case.assert_element(
            "//*[@js-collapsible_list-bulk_controls]",
            by=By.XPATH,
        )

    def assert_bulk_button_collapse_all(self) -> None:
        self.test_case.assert_element(
            '//*[@js-collapsible_list-bulk_controls]//*[@data-bulk="collapse"]',
            by=By.XPATH,
        )

    def assert_bulk_button_expand_all(self) -> None:
        self.test_case.assert_element(
            '//*[@js-collapsible_list-bulk_controls]//*[@data-bulk="expand"]',
            by=By.XPATH,
        )

    # assert global list state

    def assert_all_is_expanded(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-handler="collapsed"]',
            by=By.XPATH,
        )

    def assert_all_is_collapsed(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-handler="expanded"]',
            by=By.XPATH,
        )

    # assert single item state

    def assert_is_expanded(self, string: str) -> None:
        self.test_case.assert_element(
            f'//a[contains(., "{string}")]/../*[@data-handler="expanded"]',
            by=By.XPATH,
        )

    def assert_is_collapsed(self, string: str) -> None:
        self.test_case.assert_element(
            f'//a[contains(., "{string}")]/../*[@data-handler="collapsed"]',
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
            f'//a[contains(., "{string}")]/../*[@data-handler]',
        )

    def do_bulk_collapse_branch(self, string: str) -> None:
        self.test_case.double_click(
            f'//a[contains(., "{string}")]/../*[@data-handler="expanded"]',
            by=By.XPATH,
        )

    def do_bulk_expand_branch(self, string: str) -> None:
        self.test_case.double_click(
            f'//a[contains(., "{string}")]/../*[@data-handler="collapsed"]',
            by=By.XPATH,
        )

    def do_bulk_collapse_branch_with_key(self, string: str) -> None:
        # bulk collapse by SHIFT + click.
        element = self.test_case.find_element(
            f'//a[contains(., "{string}")]/../*[@data-handler="expanded"]',
            by=By.XPATH,
        )
        ActionChains(self.test_case.driver).key_down(Keys.SHIFT).click(
            element
        ).key_up(Keys.SHIFT).perform()

    def do_bulk_expand_branch_with_key(self, string: str) -> None:
        # bulk expand by SHIFT + click.
        element = self.test_case.find_element(
            f'//a[contains(., "{string}")]/../*[@data-handler="collapsed"]',
            by=By.XPATH,
        )
        ActionChains(self.test_case.driver).key_down(Keys.SHIFT).click(
            element
        ).key_up(Keys.SHIFT).perform()

    def do_bulk_collapse_all(self) -> None:
        self.test_case.click_xpath(
            '//*[@js-collapsible_list-bulk_controls]//*[@data-bulk="collapse"]',
        )

    def do_bulk_expand_all(self) -> None:
        self.test_case.click_xpath(
            '//*[@js-collapsible_list-bulk_controls]//*[@data-bulk="expand"]',
        )

    def do_undo_from(self, role: str) -> None:
        self.test_case.click_xpath(
            "//*[@js-collapsible_list-bulk_controls]"
            f'//*[@data-bulk="{role}"][@data-mode="undo"]'
        )

    def do_undo_from_collapse_all(self) -> None:
        self.test_case.click_xpath(
            "//*[@js-collapsible_list-bulk_controls]"
            '//*[@data-bulk="collapse"][@data-mode="undo"]'
        )

    def do_undo_from_expand_all(self) -> None:
        self.test_case.click_xpath(
            "//*[@js-collapsible_list-bulk_controls]"
            '//*[@data-bulk="expand"][@data-mode="undo"]'
        )

    def assert_handler_has_undo(self, role: str) -> None:
        # role is "collapse" or "expand"
        self.test_case.assert_element(
            (
                "//*[@js-collapsible_list-bulk_controls]"
                f"//*[@data-bulk='{role}'][@data-mode='undo']"
            ),
            by=By.XPATH,
        )

    def assert_handler_has_not_undo(self, role: str) -> None:
        # role is "collapse" or "expand"
        self.test_case.assert_element(
            (
                "//*[@js-collapsible_list-bulk_controls]"
                f"//*[@data-bulk='{role}'][@data-mode='bulk']"
            ),
            by=By.XPATH,
        )
        self.test_case.assert_element(
            (
                "//*[@js-collapsible_list-bulk_controls]"
                f"//*[@data-bulk='{role}'][not(@data-mode='undo')]"
            ),
            by=By.XPATH,
        )
