from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.node.node import Node
from tests.end2end.helpers.constants import NODE_1
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)


class Requirement(Node):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # Specific methods

    def assert_is_requirement(self, node_order: int = NODE_1) -> None:
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement",
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

    def assert_requirement_uid_contains(
        self,
        uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='UID']"
            f"[contains(., '{uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_child_link(
        self,
        child_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='child links']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_parent_link(
        self,
        parent_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='parent links']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_child_link(
        self,
        child_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element_not_present(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='child links']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_parent_link(
        self,
        parent_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element_not_present(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='parent links']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    # forms

    def do_open_form_edit_requirement(
        self, field_order: int = NODE_1
    ) -> Form_EditRequirement:
        self.test_case.hover_and_click(
            hover_selector=f"(//sdoc-node)[{field_order}]",
            click_selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)
