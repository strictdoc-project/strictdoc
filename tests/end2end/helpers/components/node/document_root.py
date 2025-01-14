from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.node.node import Node
from tests.end2end.helpers.screens.document.form_edit_config import (
    Form_EditConfig,
)


class DocumentRoot(Node):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        xpath = "//sdoc-node[@data-testid='node-root']"
        super().__init__(test_case, xpath)

    def assert_is_root_node(self) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}",
            by=By.XPATH,
        )

    def assert_root_node_is_editable(self) -> None:
        """For the root node.
        Should have the attribute and the menu button (may be invisible).
        """
        # should have the attribute
        self.test_case.assert_attribute(
            f"{self.node_xpath}",
            "data-editable_node",
            "on",
            by=By.XPATH,
        )
        # should have the menu button (may be invisible)
        self.test_case.assert_element_present(
            f"{self.node_xpath}//*[@data-testid='document-edit-config-action']",
            by=By.XPATH,
        )

    # Assert fields content: named methods

    def assert_document_title_contains(self, text: str) -> None:
        assert isinstance(text, str)
        self.test_case.assert_element(
            f"{self.node_xpath}/*[@data-testid='document-title']"
            f"[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_document_uid_contains(self, text: str) -> None:
        assert isinstance(text, str)
        self.test_case.assert_element(
            f"{self.node_xpath}//*[@data-testid='document-config-uid-label']"
            "[contains(., 'UID')]",
            by=By.XPATH,
        )
        self.test_case.assert_element(
            f"{self.node_xpath}//*[@data-testid='document-config-uid-field']"
            f"[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_document_version_contains(self, text: str) -> None:
        assert isinstance(text, str)
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//*[@data-testid='document-config-version-label']"
            "[contains(., 'VERSION')]",
            by=By.XPATH,
        )
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//*[@data-testid='document-config-version-field']"
            f"[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_document_classification_contains(self, text: str) -> None:
        assert isinstance(text, str)
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//*[@data-testid='document-config-classification-label']"
            "[contains(., 'CLASSIFICATION')]",
            by=By.XPATH,
        )
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//*[@data-testid='document-config-classification-field']"
            f"[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_document_abstract_contains(self, text: str) -> None:
        assert isinstance(text, str)
        self.test_case.assert_element(
            f"{self.node_xpath}/*[@data-testid='document-abstract']"
            f"[contains(., '{text}')]",
            by=By.XPATH,
        )

    # forms

    def do_open_form_edit_config(self) -> Form_EditConfig:
        self.test_case.hover_and_click(
            hover_selector="//*[@data-testid='node-root']",
            click_selector=(
                "//*[@data-testid='node-root']"
                "//*[@data-testid='document-edit-config-action']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditConfig(self.test_case)
