from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.document_tree.form_add_document import (
    Form_AddDocument,
)


class Screen_DocumentTree:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_text("PROJECT INDEX")

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
    # TODO: data-testid="tree-import-reqif-action"
    # TODO: data-testid="form-reqif_file-field"
    # TODO: data-testid="tree-export-reqif-action"
