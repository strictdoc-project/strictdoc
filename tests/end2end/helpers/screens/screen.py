from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.constants import NBSP, NODE_0, NODE_1


class Screen:  # pylint: disable=invalid-name, too-many-public-methods
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_header_document_title(self, document_title: str) -> None:
        self.test_case.assert_element(
            "//*[@class='header__document_title']"
            f"[contains(., '{document_title}')]",
            by=By.XPATH,
        )

    def assert_text(self, text: str) -> None:
        self.test_case.assert_text(text)

    def assert_no_text(self, text: str) -> None:
        self.test_case.assert_element_not_present(
            f"//*[contains(., '{text}')]", by=By.XPATH
        )

    # Assert fields content:
    # Method with the 'field_name' can be used,
    # but named methods are recommended.

    def assert_xpath_contains(self, xpath: str, text: str) -> None:
        # screen shared
        self.test_case.assert_element(
            f"{xpath}[contains(., '{text}')]", by=By.XPATH
        )


