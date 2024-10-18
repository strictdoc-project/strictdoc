from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.search.search import Screen_SearchResults


class Screen_ProjectStatistics:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def do_click_on_search_link(self, test_id: str) -> Screen_SearchResults:
        self.test_case.click_xpath(
            f'//a[@data-testid="{test_id}"]',
        )
        return Screen_SearchResults(self.test_case)

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="project-statistics"]',
            by=By.XPATH,
        )
        self.assert_no_js_and_404_errors()

    def assert_no_js_and_404_errors(self) -> None:
        self.test_case.assert_no_404_errors()
        self.test_case.assert_no_js_errors()
