from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Screen_SourceFileCoverage:
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="source-file"]',
            by=By.XPATH,
        )
        self.test_case.wait_for_ready_state_complete()
        self.assert_no_js_errors()

    def assert_contains_text(self, text) -> None:
        self.test_case.assert_element(
            f"//*[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_no_js_errors(self) -> None:
        self.test_case.assert_no_js_errors()
