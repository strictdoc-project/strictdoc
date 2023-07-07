# pylint: disable=invalid-name
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.exception_handler import (
    handle_selenium_exceptions,
)


class Form:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # Base

    def assert_on_form(self) -> None:
        self.test_case.assert_element(
            "//sdoc-form",
            by=By.XPATH,
        )

    def assert_on_modal(self) -> None:
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )

    # Assert field content

    def assert_error(self, message: str) -> None:
        self.test_case.assert_element(
            f"//sdoc-form-error[contains(., '{message}')]", by=By.XPATH
        )

    def assert_contenteditable_contains(self, text: str) -> None:
        self.test_case.assert_element(
            f"//sdoc-contenteditable[contains(., '{text}')]", by=By.XPATH
        )

    def assert_xpath_contains(self, xpath: str, text: str) -> None:
        self.test_case.assert_element(
            f"{xpath}[contains(., '{text}')]", by=By.XPATH
        )

    def assert_testid_contains(self, testid: str, text: str) -> None:
        self.test_case.assert_element(
            f"//*[@{testid}][contains(., '{text}')]", by=By.XPATH
        )

    # Work with fields containers

    def do_add_field(self, field_name: str = "") -> None:
        assert isinstance(field_name, str)
        self.test_case.click_xpath(
            f"//*[@data-testid='form-add-{field_name}-field-action']"
        )

    def do_delete_field(self, field_name: str, field_order: int = 1) -> None:
        assert isinstance(field_name, str)
        self.test_case.click_xpath(
            f"(//*[@data-testid='form-delete-{field_name}-field-action'])"
            f"[{field_order}]"
        )

    # MOVE fields

    def do_move_field_up(self, field_name: str = "") -> None:
        assert isinstance(field_name, str)
        self.test_case.click_xpath(
            f"(//*[@data-testid='form-move-up-{field_name}-field-action'])"
        )

    def do_move_field_down(self, field_name: str = "") -> None:
        assert isinstance(field_name, str)
        self.test_case.click_xpath(
            f"(//*[@data-testid='form-move-down-{field_name}-field-action'])"
        )

    # Work with fields content

    def do_fill_in(
        self, field_name: str, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_name, str)
        assert isinstance(field_value, str)

        field_order_str = "last()" if field_order == -1 else str(field_order)

        self.test_case.type(
            (
                f"(//*[@data-testid='form-{field_name}-field'])"
                f"[{field_order_str}]"
            ),
            f"{field_value}",
            by=By.XPATH,
        )

    def do_clear_field(self, field_name: str, field_order: int = 1) -> None:
        assert isinstance(field_name, str)
        # HACK: The only way the field is actually cleared.
        self.test_case.type(
            f"(//*[@data-testid='form-{field_name}-field'])[{field_order}]",
            "1",
            by=By.XPATH,
        )
        this_field = self.test_case.find_visible_elements(
            f"//*[@data-testid='form-{field_name}-field']"
        )[0]
        this_field.send_keys(Keys.BACKSPACE)

    # Save/Cancel

    def do_form_cancel(self) -> None:
        with handle_selenium_exceptions():
            self.test_case.click_xpath('//*[@data-testid="form-cancel-action"]')
            self.test_case.assert_element_not_present(
                '//*[@data-testid="form-cancel-action"]'
            )

    def do_form_submit(self) -> None:
        with handle_selenium_exceptions():
            self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')
            self.test_case.assert_element_not_present(
                '//*[@data-testid="form-submit-action"]'
            )

    def do_form_submit_and_catch_error(self, message: str) -> None:
        with handle_selenium_exceptions():
            self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')
            self.test_case.assert_element(
                "//sdoc-form-error",
                by=By.XPATH,
            )
            self.test_case.assert_text(f"{message}")
