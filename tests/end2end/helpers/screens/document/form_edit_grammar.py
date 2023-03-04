# pylint: disable=invalid-name
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Form_EditGrammar:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_modal(self) -> None:
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )

    def assert_on_grammar(self) -> None:
        self.test_case.assert_element(
            '//*[@id="document__editable_grammar_fields"]',
            by=By.XPATH,
        )

    def do_grammar_add_field(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="form-add-grammar-field-action"]'
        )

    def do_fill_in(
        self, field_name: str, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_name, str)
        assert isinstance(field_value, str)

        field_order_str = "last()" if field_order == -1 else str(field_order)

        self.test_case.type(
            (
                "(//*["
                f"@data-testid='form-document_grammar[{field_name}]-field'"
                f"])[{field_order_str}]"
            ),
            f"{field_value}",
            by=By.XPATH,
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
