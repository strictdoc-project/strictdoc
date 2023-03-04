# pylint: disable=invalid-name
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Form_EditConfig:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_form(self) -> None:
        self.test_case.assert_element(
            "//sdoc-form",
            by=By.XPATH,
        )

    def assert_error(self, message: str) -> None:
        self.test_case.assert_element(
            "//sdoc-form-error",
            by=By.XPATH,
        )
        self.test_case.assert_text(f"{message}")

    def assert_field_content(self, message: str) -> None:
        self.test_case.assert_element(
            "//sdoc-contenteditable",
            by=By.XPATH,
        )
        self.test_case.assert_text(f"{message}")

    def do_fill_in(
        self, field_name: str, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_name, str)
        assert isinstance(field_value, str)

        self.test_case.type(
            f"(//*[@data-testid='form-document[{field_name}]-field'])"
            f"[{field_order}]",
            f"{field_value}",
            by=By.XPATH,
        )

    def do_clear_field(self, field_name: str, field_order: int = 1) -> None:
        # HACK: The only way the field is actually cleared.
        self.test_case.type(
            f"(//*[@data-testid='form-document[{field_name}]-field'])"
            f"[{field_order}]",
            "1",
            by=By.XPATH,
        )
        this_field = self.test_case.find_visible_elements(
            f"//*[@data-testid='form-document[{field_name}]-field']"
        )[0]
        this_field.send_keys(Keys.BACKSPACE)

    def do_form_submit_and_catch_error(self, message: str) -> None:
        self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')
        self.test_case.assert_element(
            "//sdoc-form-error",
            by=By.XPATH,
        )
        self.test_case.assert_text(f"{message}")

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
