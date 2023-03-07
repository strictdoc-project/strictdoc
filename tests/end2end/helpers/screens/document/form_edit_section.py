# pylint: disable=invalid-name
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.form.form import Form


class Form_EditSection(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def do_fill_in_title(self, field_value: str) -> None:
        assert isinstance(field_value, str)

        self.test_case.type(
            "(//*[@data-testid='form-section_title-field'])",
            f"{field_value}",
            by=By.XPATH,
        )

    def do_fill_in_text(self, field_value: str) -> None:
        assert isinstance(field_value, str)

        self.test_case.type(
            "(//*[@data-testid='form-section_content-field'])",
            f"{field_value}",
            by=By.XPATH,
        )
