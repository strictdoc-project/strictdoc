from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen


class Screen_ErrorPage(Screen):
    def __init__(self, test_case: BaseCase) -> None:
        super().__init__(test_case)

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="error-page"]',
            by=By.XPATH,
        )
        self.test_case.wait_for_ready_state_complete()

    def assert_error_code(self, error_code: int) -> None:
        self.test_case.assert_element(
            f'//*[@data-testid="error-{error_code}"]',
            by=By.XPATH,
        )

    def do_click_home_page_link(self) -> None:
        self.test_case.click_xpath('//*[@data-testid="error-home-page-link"]')

    def do_click_nav_project_index_link(self) -> None:
        self.test_case.click_xpath(
            '//a[@data-testid="project-tree-link-project-index"]'
        )
