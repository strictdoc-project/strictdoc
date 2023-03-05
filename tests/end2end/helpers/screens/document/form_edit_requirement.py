# pylint: disable=invalid-name
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Form_EditRequirement:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_form(self) -> None:
        self.test_case.assert_element(
            "//sdoc-form",
            by=By.XPATH,
        )

    def assert_form_has_no_comments(self) -> None:
        self.test_case.assert_element_not_present(
            "(//*[@data-testid='form-requirement[COMMENT]-field'])"
        )

    def do_fill_in(
        self, field_name: str, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_name, str)
        assert isinstance(field_value, str)

        self.test_case.type(
            f"(//*[@data-testid='form-requirement[{field_name}]-field'])"
            f"[{field_order}]",
            f"{field_value}",
            by=By.XPATH,
        )

    def do_delete_comment(self, field_order: int = 1) -> None:
        self.test_case.click_xpath(
            "(//*[@data-testid="
            "'form-delete-requirement[COMMENT]-field-action'])"
            f"[{field_order}]"
        )

    def do_form_add_field_comment(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="form-add-comment-field-action"]'
        )

    def do_form_submit(self) -> None:
        self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')
        self.test_case.assert_element_not_present(
            '//*[@data-testid="form-submit-action"]'
        )

    def do_form_cancel(self) -> None:
        self.test_case.click_xpath('//*[@data-testid="form-cancel-action"]')
        self.test_case.assert_element_not_present(
            '//*[@data-testid="form-cancel-action"]'
        )
