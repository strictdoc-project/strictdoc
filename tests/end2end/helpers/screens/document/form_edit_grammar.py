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

    def do_click_back_to_element_list(self) -> None:
        self.test_case.click_xpath(
            "//a[@data-testid='back-link-grammar-element']"
        )

    def get_existing_mid_by_field_name(self, field_name: str) -> MID:
        xpath = f"//*[@data-testid='form-field-reserved_field_name' and text() = '{field_name}']"
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
        any_grammar_field_xpath = (
            "//*[@data-testid='form-field-reserved_field_name']"
        )
        grammar_fields_number = len(
            self.test_case.find_elements(any_grammar_field_xpath, by=By.XPATH)
        )
        new_grammar_field_ordinal_number = grammar_fields_number + 1

        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-grammar-field']"
        )

        new_grammar_field_xpath = (
            f"({any_grammar_field_xpath})[{new_grammar_field_ordinal_number}]"
        )

        element = self.test_case.find_element(new_grammar_field_xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_add_grammar_relation(self) -> MID:
        any_relation_xpath = "//*[@data-testid='grammar-form-relation-row']"
        relations_number = len(
            self.test_case.find_elements(any_relation_xpath, by=By.XPATH)
        )
        new_relation_ordinal_number = relations_number + 1

        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-grammar-relation']"
        )

        xpath = f"({any_relation_xpath})[{new_relation_ordinal_number}]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_fill_in_grammar_field_mid(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(
            mid, "form-field-reserved_field_name", field_value
        )

    def do_fill_in_grammar_field_human_title_mid(
        self, mid: MID, field_value: str
    ) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(
            mid, "form-field-reserved_field_human_title", field_value
        )

    def do_select_grammar_relation_type(self, mid, relation_type):
        assert isinstance(mid, MID)
        assert isinstance(relation_type, str)

        xpath = f"(//*[@mid='{mid}' and @data-testid='select-relation-type'])"

        self.test_case.select_option_by_value(xpath, relation_type)

    def do_fill_in_grammar_relation_role(self, mid, field_value):
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(mid, "form-field-relation-role", field_value)

    def do_move_grammar_field_up(self, mid: MID) -> None:
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid}' "
            "and "
            "@data-testid='form-move-up-field-action-custom-field'])"
        )

    def do_move_grammar_field_down(self, mid: MID) -> None:
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid}' "
            "and "
            "@data-testid='form-move-down-field-action-custom-field'])"
        )

    def do_delete_grammar_field(self, mid: MID) -> None:
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid}' "
            "and "
            "@data-testid='form-delete-field-action-custom-field'])"
        )

    def do_delete_grammar_relation(self, mid: MID):
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid}' "
            "and "
            "@data-testid='form-delete-field-action-relation'])"
        )
