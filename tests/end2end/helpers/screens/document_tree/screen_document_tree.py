from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.document_tree.form_add_document import (
    Form_AddDocument,
)
from tests.end2end.helpers.screens.document_tree.form_import_reqif import (
    Form_ImportReqIF,
)


class Screen_DocumentTree:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="document-tree"]',
            by=By.XPATH,
        )

    def assert_header_project_name(self, project_title: str) -> None:
        self.test_case.assert_element(
            "//*[@class='header__project_name']"
            f"[contains(., '{project_title}')]",
            by=By.XPATH,
        )

    def assert_contains_document(self, document_title: str) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='tree-file-link']"
            f"//*[contains(., '{document_title}')]",
            by=By.XPATH,
        )

    def assert_empty_tree(self) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='document-tree-empty-text']"
            "[contains(., 'The document tree has no documents yet.')]",
            by=By.XPATH,
        )

    def do_click_on_first_document(self) -> Screen_Document:
        self.test_case.click_xpath('//*[@data-testid="tree-file-link"]')
        return Screen_Document(self.test_case)

    def do_click_on_the_document(self, doc_order: int = 1) -> Screen_Document:
        self.test_case.click_xpath(
            f"(//*[@data-testid='tree-file-link'])[{doc_order}]"
        )
        return Screen_Document(self.test_case)

    # Add new document

    def do_open_modal_form_add_document(self) -> Form_AddDocument:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            '(//*[@data-testid="tree-add-document-action"])'
        )
        self.test_case.assert_element("//sdoc-modal", by=By.XPATH)
        return Form_AddDocument(self.test_case)

    # Import / Export

    def do_open_modal_import_reqif(self) -> Form_ImportReqIF:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            '//*[@data-testid="tree-import-reqif-action"]'
        )
        self.test_case.assert_element("//sdoc-modal", by=By.XPATH)
        return Form_ImportReqIF(self.test_case)

    def do_export_reqif(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="tree-export-reqif-action"]'
        )
