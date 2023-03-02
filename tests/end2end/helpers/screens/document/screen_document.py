from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

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

    def assert_is_document_title(self, document_title: str) -> None:
        self.test_case.assert_text(document_title)

    def assert_text(self, text: str) -> None:
        self.test_case.assert_text(text)

    def assert_requirement_style_simple(self) -> None:
        # Make sure that the normal (not table-based) requirement is rendered.
        self.test_case.assert_element(
            '//sdoc-node[@data-testid="node-requirement-simple"]',
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
