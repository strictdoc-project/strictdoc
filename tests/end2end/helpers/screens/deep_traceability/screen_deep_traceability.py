from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Screen_Deep_Traceability:  # pylint: disable=invalid-name, too-many-public-methods
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self):
        self.test_case.assert_element(
            '//body[@data-viewtype="deep_traceability"]',
            by=By.XPATH,
        )

    def assert_empty_document(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="trace-deep-main-placeholder"]'
        )

    def assert_not_empty_document(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="trace-deep-main-placeholder"]'
        )

    def assert_text(self, text: str) -> None:
        # screen shared
        self.test_case.assert_text(text)

    def assert_no_text(self, text: str) -> None:
        # screen shared
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


