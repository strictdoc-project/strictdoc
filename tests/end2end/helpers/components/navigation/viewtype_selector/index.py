from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.deep_traceability.screen_deep_traceability import (
    Screen_Deep_Traceability,
)


class ViewType_Selector:  # pylint: disable=invalid-name, too-many-public-methods
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_viewtype_handler(self):
        self.test_case.assert_element(
            "//div[@id='viewtype_handler']",
            by=By.XPATH,
        )

    def do_open_viewtype_selector(self) -> None:
        self.test_case.click_xpath(
            "(//div[@id='viewtype_handler']"
        )

    def do_go_to_document(self) -> Screen_Document:
        self.do_open_viewtype_selector()
        self.test_case.click_xpath(
            '(//*[@data-viewtype_link="document"]'
        )
        return Screen_Document(self.test_case)

    def do_go_to_deep_traceability(self) -> Screen_Deep_Traceability:
        self.do_open_viewtype_selector()
        self.test_case.click_xpath(
            '(//*[@data-viewtype_link="deep_traceability"]'
        )
        return Screen_Deep_Traceability(self.test_case)
