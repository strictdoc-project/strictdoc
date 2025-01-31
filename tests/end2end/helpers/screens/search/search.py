from selenium import webdriver
from selenium.webdriver.common.by import By

from tests.end2end.helpers.screens.screen import Screen


class Screen_SearchResults(Screen):  # pylint: disable=invalid-name
    def do_click_on_search_requirements(self):
        self.test_case.click_xpath(
            '//a[@data-testid="node.is_requirement"]',
        )

    def get_search_error_msg(self):
        return self.test_case.find_element(
            By.XPATH, "//div[@class='sdoc-form-error']"
        ).text

    def assert_nr_results(self, nr_results: int):
        content = (
            f"Found {nr_results} results."
            if nr_results > 0
            else "Nothing matching the query was found."
        )
        self.test_case.assert_element(
            f"//div[@class='sdoc-form-success'][contains(., '{content}')]",
            by=By.XPATH,
        )


class Screen_Search(Screen):  # pylint: disable=invalid-name
    def do_click_on_search_requirements(self) -> Screen_SearchResults:
        self.test_case.click_xpath(
            '//a[@data-testid="node.is_requirement"]',
        )
        return Screen_SearchResults(self.test_case)

    def do_click_on_search_sections(self) -> Screen_SearchResults:
        self.test_case.click_xpath(
            '//a[@data-testid="node.is_section"]',
        )
        return Screen_SearchResults(self.test_case)

    def do_search(self, query) -> Screen_SearchResults:
        textBox = self.test_case.driver.find_element(
            By.XPATH, "//input[@id='q']"
        )
        textBox.clear()
        textBox.send_keys(query)
        self.test_case.click_xpath(
            '//button[@data-testid="form-submit-action"]',
        )
        return Screen_SearchResults(self.test_case)
