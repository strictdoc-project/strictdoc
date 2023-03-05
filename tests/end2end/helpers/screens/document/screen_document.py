from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.form_edit_config import (
    Form_EditConfig,
)
from tests.end2end.helpers.screens.document.form_edit_grammar import (
    Form_EditGrammar,
)
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)


class Screen_Document:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self):
        self.test_case.assert_element(
            '//body[@data-viewtype="document"]',
            by=By.XPATH,
        )

    def assert_empty_document(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="document-placeholder"]'
        )

    def assert_not_empty_document(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="document-placeholder"]'
        )

    def assert_is_document_title(self, document_title: str) -> None:
        self.test_case.assert_text(document_title)

    def assert_text(self, text: str) -> None:
        self.test_case.assert_text(text)

    def assert_no_text(self, text: str) -> None:
        self.test_case.assert_element_not_present(
            f"//*[contains(., '{text}')]", by=By.XPATH
        )

    def assert_requirement_style_simple(self) -> None:
        # Make sure that the normal (not table-based) requirement is rendered.
        self.test_case.assert_element(
            '//sdoc-node[@data-testid="node-requirement-simple"]',
            by=By.XPATH,
        )

    def assert_requirement_style_table(self) -> None:
        # Make sure that the table-based requirement is rendered.
        self.test_case.assert_element(
            '//sdoc-node[@data-testid="node-requirement-table"]',
            by=By.XPATH,
        )

    def assert_toc_contains_string(self, string: str) -> None:
        self.test_case.assert_element(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]"
        )

    def do_open_edit_form(self) -> Form_EditRequirement:
        self.test_case.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_open_config_form(self) -> Form_EditConfig:
        self.test_case.hover_and_click(
            hover_selector="(//sdoc-node)[1]",
            click_selector=(
                '(//sdoc-node)[1]//*[@data-testid="document-edit-config-action"]'  # noqa: E501
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditConfig(self.test_case)

    def do_open_edit_grammar_modal(self) -> Form_EditGrammar:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            '(//*[@data-testid="document-edit-grammar-action"])'
        )
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )
        return Form_EditGrammar(self.test_case)

    def do_export_reqif(self) -> None:
        self.test_case.click_xpath(
            '(//*[@data-testid="document-export-reqif-action"])'
        )
