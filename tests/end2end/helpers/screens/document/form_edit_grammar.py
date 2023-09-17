# pylint: disable=invalid-name

from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from strictdoc.helpers.mid import MID
from tests.end2end.helpers.form.form import Form


class Form_EditGrammar(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def assert_on_grammar(self) -> None:
        self.test_case.assert_element(
            '//*[@id="document__editable_grammar_fields"]',
            by=By.XPATH,
        )

    def get_existing_mid_by_field_name(self, field_name: str) -> MID:
        xpath = f"//*[@data-testid='form-field-custom-field' and text() = '{field_name}']"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def get_existing_relation_mid(self, order: int = -1) -> MID:
        order_argument = "last()" if order == -1 else str(order)
        xpath = (
            f"(//*[@data-testid='grammar-form-relation-row'])[{order_argument}]"
        )
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_add_grammar_field(self) -> MID:
        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-grammar-field']"
        )
        xpath = "(//*[@data-testid='form-field-custom-field'])[last()]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_add_grammar_relation(self) -> MID:
        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-grammar-relation']"
        )
        xpath = "(//*[@data-testid='grammar-form-relation-row'])[last()]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_fill_in_grammar_field_mid(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(mid, "form-field-custom-field", field_value)

    def do_fill_in_grammar_relation_role(self, mid, field_value):
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(mid, "form-field-relation-role", field_value)

    def do_move_grammar_field_up(self, mid: MID) -> None:
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid.get_string_value()}' "
            "and "
            "@data-testid='form-move-up-field-action-custom-field'])"
        )

    def do_move_grammar_field_down(self, mid: MID) -> None:
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid.get_string_value()}' "
            "and "
            "@data-testid='form-move-down-field-action-custom-field'])"
        )

    def do_delete_grammar_field(self, mid: MID) -> None:
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid.get_string_value()}' "
            "and "
            "@data-testid='form-delete-field-action-custom-field'])"
        )

    def do_delete_grammar_relation(self, mid: MID):
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid.get_string_value()}' "
            "and "
            "@data-testid='form-delete-field-action-relation'])"
        )
