# pylint: disable=invalid-name
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.form.form import Form


class Form_EditConfig(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # Fill in:
    # Method with the 'field_name' can be used,
    # but named methods are recommended.

    def do_fill_in_config_field(
            self, field_name: str, field_value: str, field_order: int = 1
        ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in(f"document[{field_name}]", field_value, field_order)

    # Fill in: named methods

    def do_fill_in_document_uid(
            self, field_value: str, field_order: int = 1
        ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in(f"document[UID]", field_value, field_order)

    def do_fill_in_document_title(
            self, field_value: str, field_order: int = 1
        ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in(f"document[TITLE]", field_value, field_order)

    def do_fill_in_document_version(
            self, field_value: str, field_order: int = 1
        ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in(f"document[VERSION]", field_value, field_order)

    def do_fill_in_document_classification(
            self, field_value: str, field_order: int = 1
        ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in(
            f"document[CLASSIFICATION]", field_value, field_order
        )

    def do_fill_in_document_abstract(
            self, field_value: str, field_order: int = 1
        ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in(f"document[FREETEXT]", field_value, field_order)

    # Clear:
    # Method with the 'field_name' can be used,
    # but named methods are recommended.

    def do_clear_config_field(
            self, field_name: str, field_order: int = 1
        ) -> None:
        super().do_clear_field(f"document[{field_name}]", field_order)

    # Clear: named methods

    def do_clear_document_uid(self, field_order: int = 1) -> None:
        super().do_clear_field(f"document[UID]", field_order)

    def do_clear_document_title(self, field_order: int = 1) -> None:
        super().do_clear_field(f"document[TITLE]", field_order)

    def do_clear_document_version(self, field_order: int = 1) -> None:
        super().do_clear_field(f"document[VERSION]", field_order)

    def do_clear_document_classification(self, field_order: int = 1) -> None:
        super().do_clear_field(f"document[CLASSIFICATION]", field_order)

    def do_clear_document_abstract(self, field_order: int = 1) -> None:
        super().do_clear_field(f"document[FREETEXT]", field_order)
