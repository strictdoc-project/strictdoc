from datetime import datetime

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.form_edit_grammar import (
    Form_EditGrammar,
)
from tests.end2end.helpers.screens.screen import Screen


class Screen_Document(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # overridden for Screen_Document

    def assert_on_screen_document(self) -> None:
        super().assert_on_screen("document")

    def assert_empty_document(self) -> None:
        super().assert_empty_view("document-root-placeholder")

    def assert_not_empty_document(self) -> None:
        super().assert_not_empty_view("document-root-placeholder")

    def assert_target_by_anchor(self, anchor) -> None:
        # check if the link was successfully clicked
        # and that the target is highlighted
        targeted_anchor = f"sdoc-anchor[id='{anchor}']:target"
        self.test_case.assert_element_present(targeted_anchor)

    # Actions on the page

    def do_export_reqif(self) -> None:
        self.test_case.click_xpath(
            '(//*[@data-testid="document-export-reqif-action"])'
        )

    # Open forms

    def do_open_modal_form_edit_grammar(self) -> Form_EditGrammar:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            '(//*[@data-testid="document-edit-grammar-action"])'
        )
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )
        return Form_EditGrammar(self.test_case)

    def do_drag_first_toc_node_to_the_second(self) -> None:
        xpath_first_toc_node = '(//li[@draggable="true"])[1]'
        xpath_second_toc_node = '(//li[@draggable="true"])[2]'

        first_toc_node = self.test_case.find_element(xpath_first_toc_node)
        first_toc_node_mid = first_toc_node.get_attribute("data-nodeid")

        second_toc_node = self.test_case.find_element(xpath_second_toc_node)
        second_toc_node_mid = second_toc_node.get_attribute("data-nodeid")

        self.test_case.drag_and_drop(
            xpath_first_toc_node, xpath_second_toc_node
        )

        """
        Drag and drop action takes some time before server/Turbo sends
        an updated AJAX HTML template back. Sometimes a
        StaleElementReferenceException is thrown by Selenium because it still
        finds an old element as it is being moved. To solve this, set a timeout
        to wait some time until the new TOC is rendered.
        """
        start_time = datetime.now()
        while True:
            new_root_node = self.test_case.find_element(
                f'(//li[@data-nodeid="{second_toc_node_mid}"])[1]'
            )
            moved_node = self.test_case.find_element(
                f'(//li[@data-nodeid="{first_toc_node_mid}"])[1]'
            )

            try:
                if new_root_node.location["y"] < moved_node.location["y"]:
                    break
            except StaleElementReferenceException:
                # The element is the one from an old TOC. Keep waiting.
                self.test_case.sleep(0.1)

            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "StrictDoc custom timeout: Moving element in the TOC"
                )
