# pylint: disable=invalid-name

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from strictdoc.helpers.mid import MID
from tests.end2end.helpers.form.form import Form
from tests.end2end.helpers.screens.document.form_edit_grammar import (
    Form_EditGrammar,
)


class Form_EditGrammarElements(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def assert_on_grammar(self) -> None:
        self.test_case.assert_element(
            '//*[@id="document__editable_grammar_elements"]',
            by=By.XPATH,
        )

    def assert_file_grammars_are_not_supported(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="grammar-from-file-editing-blocker-placeholder"]',
            by=By.XPATH,
        )

    def get_grammar_element(self, node_order: int = 1) -> MID:
        assert node_order >= 1, node_order

        any_grammar_field_xpath = (
            "//*[@data-testid='form-field-grammar-element']"
        )
        grammar_field_xpath = f"({any_grammar_field_xpath})[{node_order}]"
        element = self.test_case.find_element(grammar_field_xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_click_edit_grammar_element(
        self, node_order: int = 1
    ) -> Form_EditGrammar:
        assert node_order >= 1, node_order

        grammar_element_mid: MID = self.get_grammar_element(node_order)

        self.test_case.click_xpath(
            f"//a[@data-testid='edit-link-grammar-element-{grammar_element_mid}']"
        )

        return Form_EditGrammar(self.test_case)

    def do_add_grammar_element(self) -> MID:
        any_grammar_field_xpath = (
            "//*[@data-testid='form-field-grammar-element']"
        )
        grammar_fields_number = len(
            self.test_case.find_elements(any_grammar_field_xpath, by=By.XPATH)
        )
        new_grammar_field_ordinal_number = grammar_fields_number + 1

        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-grammar-element']"
        )

        new_grammar_field_xpath = (
            f"({any_grammar_field_xpath})[{new_grammar_field_ordinal_number}]"
        )

        element = self.test_case.find_element(new_grammar_field_xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_fill_in_grammar_element_mid(
        self, mid: MID, field_value: str
    ) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(mid, "form-field-grammar-element", field_value)
