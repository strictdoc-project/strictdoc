from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Confirm:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    def assert_confirm(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="confirm-message"]',
            by=By.XPATH,
        )

    def assert_confirm_requirement_delete(self) -> None:
        self.test_case.assert_element('//*[@data-testid="confirm-message"]')
        self.test_case.assert_element(
            '//*[@data-testid="confirm-action"]'
            '[contains(., "Delete requirement")]',
            by=By.XPATH,
        )

    def assert_confirm_section_delete(self) -> None:
        self.test_case.assert_element('//*[@data-testid="confirm-message"]')
        self.test_case.assert_element(
            '//*[@data-testid="confirm-action"]'
            '[contains(., "Delete section")]',
            by=By.XPATH,
        )

    def do_confirm_action(self) -> None:
        self.test_case.click(
            selector=('//*[@data-testid="confirm-action"]'),
            by=By.XPATH,
        )
