# pylint: disable=invalid-name
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.form.form import Form


class Form_EditSection(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def do_fill_in_title(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("section_title", field_value)

    def do_fill_in_text(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("section_content", field_value)
