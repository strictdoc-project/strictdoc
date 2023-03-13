from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Screen_Table:  # pylint: disable=invalid-name, too-many-public-methods
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self):
        self.test_case.assert_element(
            '//body[@data-viewtype="table"]',
            by=By.XPATH,
        )

    def assert_empty_document(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="table-main-placeholder"]'
        )

    def assert_not_empty_document(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="table-main-placeholder"]'
        )
