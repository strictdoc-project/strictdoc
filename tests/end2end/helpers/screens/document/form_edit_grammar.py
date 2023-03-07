# pylint: disable=invalid-name
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.form.form import Form


class Form_EditGrammar(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def assert_on_grammar(self) -> None:
        self.test_case.assert_element(
            '//*[@id="document__editable_grammar_fields"]',
            by=By.XPATH,
        )

    def do_add_grammar_field(self) -> None:
        super().do_add_field("grammar")

    def do_fill_in_grammar_field(
        self, field_name: str, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_name, str)
        assert isinstance(field_value, str)
        # Use data-testid="form-move-up-document_grammar[]-field-action"
        # for the newly added fields.
        super().do_fill_in(
            f"document_grammar[{field_name}]", field_value, field_order
        )

    def do_move_grammar_field_up(self, field_name: str = "") -> None:
        # Use data-testid="form-move-up-document_grammar[]-field-action"
        # for the newly added fields.
        super().do_move_field_up(f"document_grammar[{field_name}]")

    def do_move_grammar_field_down(self, field_name: str = "") -> None:
        # Use data-testid="form-move-up-document_grammar[]-field-action"
        # for the newly added fields.
        super().do_move_field_down(f"document_grammar[{field_name}]")

    def do_delete_grammar_field(self, field_name: str) -> None:
        super().do_delete_field(f"document_grammar[{field_name}]")
