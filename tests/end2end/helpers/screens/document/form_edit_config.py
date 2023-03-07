# pylint: disable=invalid-name
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.form.form import Form


class Form_EditConfig(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # Assert fields:
    # Parent class method with the 'xpath' or 'testid' can be used,
    # but named methods are recommended.
    # Assert: named methods:

    def assert_document_abstract_contains(self, text: str) -> None:
        assert isinstance(text, str)
        super().assert_testid_contains(
            "data-testid='form-document[FREETEXT]-field'", text
        )

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
        super().do_fill_in("document[UID]", field_value, field_order)

    def do_fill_in_document_title(
        self, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document[TITLE]", field_value, field_order)

    def do_fill_in_document_version(
        self, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document[VERSION]", field_value, field_order)

    def do_fill_in_document_classification(
        self, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document[CLASSIFICATION]", field_value, field_order)

    def do_fill_in_document_abstract(
        self, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document[FREETEXT]", field_value, field_order)

    # Clear:
    # Method with the 'field_name' can be used,
    # but named methods are recommended.

    def do_clear_config_field(
        self, field_name: str, field_order: int = 1
    ) -> None:
        super().do_clear_field(f"document[{field_name}]", field_order)

    # Clear: named methods

    def do_clear_document_uid(self, field_order: int = 1) -> None:
        super().do_clear_field("document[UID]", field_order)

    def do_clear_document_title(self, field_order: int = 1) -> None:
        super().do_clear_field("document[TITLE]", field_order)

    def do_clear_document_version(self, field_order: int = 1) -> None:
        super().do_clear_field("document[VERSION]", field_order)

    def do_clear_document_classification(self, field_order: int = 1) -> None:
        super().do_clear_field("document[CLASSIFICATION]", field_order)

    def do_clear_document_abstract(self, field_order: int = 1) -> None:
        super().do_clear_field("document[FREETEXT]", field_order)
