from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Screen_RequirementsCoverage:
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="traceability-matrix"]',
            by=By.XPATH,
        )
        self.test_case.wait_for_ready_state_complete()
        self.assert_no_js_and_404_errors()

    def assert_no_js_and_404_errors(self) -> None:
        self.test_case.assert_no_404_errors()
        self.test_case.assert_no_js_errors()
