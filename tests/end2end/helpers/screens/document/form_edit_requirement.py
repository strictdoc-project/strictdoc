# pylint: disable=invalid-name
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from strictdoc.helpers.mid import MID
from tests.end2end.helpers.form.form import Form


class Form_EditRequirement(Form):  # pylint: disable=invalid-name
    class XPATH:
        RELATION_ROW = "(//*[@data-testid='requirement-form-relation-row'])"

    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # comment actions

    def assert_form_has_no_comments(self) -> None:
        self.test_case.assert_element_not_present(
            "(//*[@data-testid='form-requirement[COMMENT]-field'])"
        )

    def do_form_add_field_comment(self) -> MID:
        any_comment_xpath = "//*[@data-testid='requirement-form-comment-row']"
        comments_number = len(
            self.test_case.find_elements(any_comment_xpath, by=By.XPATH)
        )
        new_comment_ordinal_number = comments_number + 1

        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-comment']"
        )

        xpath = f"({any_comment_xpath})[{new_comment_ordinal_number}]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        assert element_mid is not None
        assert len(element_mid) > 0
        return MID(element_mid)

    def do_delete_comment(self, field_order: int = 1) -> None:
        # TODO: update with mid
        super().do_delete_field("requirement-comment", field_order)

    def do_fill_in_field_comment(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(
            mid, "form-field-requirement-field-COMMENT", field_value
        )

    # RELATION actions

    def assert_form_has_relations(self) -> None:
        self.test_case.assert_element(Form_EditRequirement.XPATH.RELATION_ROW)

    def assert_form_has_no_relations(self) -> None:
        self.test_case.assert_element_not_present(
            Form_EditRequirement.XPATH.RELATION_ROW
        )

    def do_form_add_field_relation(self) -> MID:
        any_relation_xpath = "//*[@data-testid='requirement-form-relation-row']"
        relations_number = len(
            self.test_case.find_elements(any_relation_xpath, by=By.XPATH)
        )
        new_relation_ordinal_number = relations_number + 1

        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-relation']"
        )

        xpath = f"({any_relation_xpath})[{new_relation_ordinal_number}]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_delete_relation(self, field_order: int = 1) -> None:
        # TODO: update with mid
        super().do_delete_field("requirement-relation", field_order)

    def do_fill_in_field_relation(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(
            mid, "form-field-requirement-relation-uid", field_value
        )

    def do_select_relation_role(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)

        xpath = (
            f"(//*[@mid='{mid.get_string_value()}' "
            "and "
            "@data-testid='select-relation-typerole'])"
        )
        self.test_case.select_option_by_value(xpath, field_value)

    # Fill in the named fields.

    def do_fill_in_field_uid(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("requirement-field-UID", field_value)

    def do_fill_in_field_title(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("requirement-field-TITLE", field_value)

    def do_fill_in_field_statement(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("requirement-field-STATEMENT", field_value)

    def do_fill_in_field_rationale(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("requirement-field-RATIONALE", field_value)

    # Reset UID button

    def assert_uid_field_contains(self, string: str) -> None:
        self.test_case.assert_element_present(
            "//*[@data-testid='form-field-UID']"
            f"[contains(., '{string}')]",
            by=By.XPATH,
        )

    def assert_uid_field_does_not_contain(self, string: str) -> None:
        self.test_case.assert_element_not_present(
            "//*[@data-testid='form-field-UID']"
            f"[contains(., '{string}')]",
            by=By.XPATH,
        )

    def assert_uid_field_has_reset_button(self) -> None:
        self.test_case.assert_element_present(
            "//*[@data-testid='reset-uid-field-action']",
            by=By.XPATH,
        )

    def assert_uid_field_has_not_reset_button(self) -> None:
        self.test_case.assert_element_not_present(
            "//*[@data-testid='reset-uid-field-action']",
            by=By.XPATH,
        )

    def do_reset_uid_field(self, field_name: str = "") -> None:
        assert isinstance(field_name, str)
        self.test_case.click_xpath("//*[@data-testid='reset-uid-field-action']")
