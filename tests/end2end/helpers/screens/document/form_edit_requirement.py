# pylint: disable=invalid-name
from seleniumbase import BaseCase

from strictdoc.helpers.mid import MID
from tests.end2end.helpers.form.form import Form


class Form_EditRequirement(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # comment actions

    def assert_form_has_no_comments(self) -> None:
        self.test_case.assert_element_not_present(
            "(//*[@data-testid='form-requirement[COMMENT]-field'])"
        )

    def do_form_add_field_comment(self) -> MID:
        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-comment']"
        )
        xpath = "(//*[@data-testid='requirement-form-comment-row'])[last()]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        assert element_mid is not None
        assert len(element_mid) > 0
        return MID(element_mid)

    def do_delete_comment(self, field_order: int = 1) -> None:
        super().do_delete_field("requirement-comment", field_order)

    def do_fill_in_field_comment(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in_mid(
            mid, "form-field-requirement-field-COMMENT", field_value
        )

    # parent-link actions

    def assert_form_has_no_parents(self) -> None:
        self.test_case.assert_element_not_present(
            "(//*[@data-testid='form-requirement[REFS_PARENT][]-field'])"
        )

    def do_form_add_field_parent_link(self) -> MID:
        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-parent-link']"
        )
        xpath = "(//*[@data-testid='requirement-form-relation-row'])[last()]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_delete_parent_link(self, field_order: int = 1) -> None:
        super().do_delete_field("requirement-relation", field_order)

    def do_fill_in_field_parent_link(self, mid: MID, field_value: str) -> None:
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
