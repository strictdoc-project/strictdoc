from selenium.webdriver.common.by import By

from tests.end2end.helpers.screens.screen import Screen


class Screen_SearchResults(Screen):  # pylint: disable=invalid-name
    def do_click_on_search_requirements(self):
        self.test_case.click_xpath(
            '//a[@data-testid="node.is_requirement"]',
        )

    def assert_nr_results(self, nr_results: int):
        content = (
            f"Found {nr_results} results."
            if nr_results > 0
            else "Nothing matching the query was found."
        )
        self.test_case.assert_element(
            "//div[@class='sdoc-form-success']" f"[contains(., '{content}')]",
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
