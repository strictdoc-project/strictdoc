from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.node.node import Node
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)


class Requirement(Node):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase, node_order: int = 1) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_order, int)
        xpath = f"(//sdoc-node[@data-testid='node-requirement'])[{node_order}]"
        super().__init__(test_case, xpath)
        self.node_order: int = node_order

    # Specific methods

    def assert_is_requirement(self) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}",
            by=By.XPATH,
        )

    # requirement style

    def assert_requirement_style_simple(self) -> None:
        """Make sure that the normal (not table-based) requirement
        is rendered."""
        self.test_case.assert_element(
            '//sdoc-requirement[@data-testid="requirement-style-simple"]',
            by=By.XPATH,
        )

    def assert_requirement_style_table(self) -> None:
        """Make sure that the table-based requirement is rendered."""
        self.test_case.assert_element(
            '//sdoc-requirement[@data-testid="requirement-style-table"]',
            by=By.XPATH,
        )

    # requirement named fields

    def assert_requirement_title(
        self,
        node_title: str,
        node_level: str = "",
    ) -> None:
        title = super().create_node_title_string(node_title, node_level)
        self.test_case.assert_element(
            f"{self.node_xpath}"
            f"//sdoc-requirement-title[contains(text(), '{title}')]",
            by=By.XPATH,
        )

    def assert_requirement_uid_contains(
        self,
        uid: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='UID']"
            f"[contains(text(), '{uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_statement_contains(
        self,
        text: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='statement']"
            f"//*[contains(text(), '{text}')]",
            by=By.XPATH,
        )

    def assert_requirement_rationale_contains(
        self,
        text: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='rationale']"
            f"//*[contains(text(), '{text}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_child_link(
        self,
        child_uid: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='child links']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_parent_link(
        self,
        parent_uid: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='parent links']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_child_link(
        self,
        child_uid: str,
    ) -> None:
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='child links']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_parent_link(
        self,
        parent_uid: str,
    ) -> None:
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='parent links']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    # forms

    def do_open_form_edit_requirement(self) -> Form_EditRequirement:
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f'{self.node_xpath}//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)
