from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Screen_SourceCoverage:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="coverage-tree"]',
            by=By.XPATH,
        )
        self.assert_no_js_and_404_errors()

    def assert_contains_text(self, text) -> None:
        self.test_case.assert_element(
            f"//*[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_no_js_and_404_errors(self) -> None:
        self.test_case.assert_no_404_errors()
        self.test_case.assert_no_js_errors()
