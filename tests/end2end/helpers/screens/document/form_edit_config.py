# pylint: disable=invalid-name
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from strictdoc.helpers.mid import MID
from tests.end2end.helpers.form.form import Form


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
            "data-testid='form-field-document[FREETEXT]'", text
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

    def do_fill_in_document_requirement_prefix(
        self, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document[PREFIX]", field_value, field_order)

    def do_fill_in_document_abstract(
        self, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_value, str)
        super().do_fill_in("document[FREETEXT]", field_value, field_order)

    # METADATA actions

    def do_form_add_field_metadata(self) -> MID:
        any_relation_xpath = (
            "//*[@data-testid='document-config-form-metadata-row']"
        )
        relations_number = len(
            self.test_case.find_elements(any_relation_xpath, by=By.XPATH)
        )
        new_relation_ordinal_number = relations_number + 1

        self.test_case.click_xpath(
            "//*[@data-testid='form-action-add-metadata-field']"
        )

        xpath = f"({any_relation_xpath})[{new_relation_ordinal_number}]"
        element = self.test_case.find_element(xpath)
        element_mid = element.get_attribute("mid")
        return MID(element_mid)

    def do_fill_in_field_name(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in(f"metadata[{mid}][name]", field_value)

    def do_fill_in_field_value(self, mid: MID, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(field_value, str)
        super().do_fill_in(f"metadata[{mid}][value]", field_value)

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
