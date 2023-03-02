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

    def do_fill_in(self, field_name: str, field_value: str) -> None:
        assert isinstance(field_name, str)
        assert isinstance(field_value, str)

        self.test_case.type(
            f"//*[@id='requirement[{field_name}]']",
            f"{field_value}",
            by=By.XPATH,
        )

    def do_form_submit(self) -> None:
        self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')
