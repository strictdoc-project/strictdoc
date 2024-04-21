from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.deep_traceability.screen_deep_traceability import (
    Screen_Deep_Traceability,
)
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.pdf.screen_pdf import Screen_PDFDocument
from tests.end2end.helpers.screens.standalone_document.screen_standalone_document import (
    Screen_StandaloneDocument,
)
from tests.end2end.helpers.screens.table.screen_table import (
    Screen_Table,
)
from tests.end2end.helpers.screens.traceability.screen_traceability import (
    Screen_Traceability,
)


class ViewType_Selector:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    def assert_is_viewtype_selector(self) -> None:
        self.assert_viewtype_handler()
        self.assert_viewtype_menu()

    def assert_viewtype_handler(self) -> None:
        self.test_case.assert_element(
            "//*[@id='viewtype_handler']",
            by=By.XPATH,
        )

    def assert_viewtype_menu(self) -> None:
        """Can be closed"""
        self.test_case.assert_element_present(
            "//*[@id='viewtype_menu']",
            by=By.XPATH,
        )

    def do_click_viewtype_handler(self) -> None:
        self.test_case.click_xpath("//*[@id='viewtype_handler']")

    def assert_viewtype_menu_opened(self) -> None:
        self.test_case.assert_element_visible(
            "//*[@id='viewtype_menu']",
            by=By.XPATH,
        )

    def assert_viewtype_menu_closed(self) -> None:
        self.test_case.assert_element_not_visible(
            "//*[@id='viewtype_menu']",
            by=By.XPATH,
        )

    # open pages

    def do_go_to_document(self) -> Screen_Document:
        self.do_click_viewtype_handler()
        self.assert_viewtype_menu_opened()
        self.test_case.click_xpath('//*[@data-viewtype_link="document"]')
        return Screen_Document(self.test_case)

    def do_go_to_table(self) -> Screen_Table:
        self.do_click_viewtype_handler()
        self.assert_viewtype_menu_opened()
        self.test_case.click_xpath('//*[@data-viewtype_link="table"]')
        return Screen_Table(self.test_case)

    def do_go_to_traceability(self) -> Screen_Traceability:
        self.do_click_viewtype_handler()
        self.assert_viewtype_menu_opened()
        self.test_case.click_xpath('//*[@data-viewtype_link="traceability"]')
        return Screen_Traceability(self.test_case)

    def do_go_to_deep_traceability(self) -> Screen_Deep_Traceability:
        self.do_click_viewtype_handler()
        self.assert_viewtype_menu_opened()
        self.test_case.click_xpath(
            '//*[@data-viewtype_link="deep_traceability"]'
        )
        return Screen_Deep_Traceability(self.test_case)

    def do_go_to_standalone_document(self) -> Screen_StandaloneDocument:
        self.do_click_viewtype_handler()
        self.assert_viewtype_menu_opened()
        self.test_case.click_xpath(
            '//*[@data-viewtype_link="standalone_document"]'
        )
        return Screen_StandaloneDocument(self.test_case)

    def do_go_to_pdf_document(self) -> Screen_PDFDocument:
        self.do_click_viewtype_handler()
        self.assert_viewtype_menu_opened()
        self.test_case.click_xpath('//*[@data-viewtype_link="html2pdf"]')
        return Screen_PDFDocument(self.test_case)
