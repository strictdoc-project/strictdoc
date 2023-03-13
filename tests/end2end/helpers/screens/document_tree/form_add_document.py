from seleniumbase import BaseCase

from tests.end2end.helpers.form.form import Form


class Form_AddDocument(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def do_fill_in_title(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document_title", field_value)

    def do_fill_in_path(self, field_value: str) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document_path", field_value)
