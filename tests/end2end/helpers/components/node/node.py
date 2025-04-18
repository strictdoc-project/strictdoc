from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.confirm import Confirm
from tests.end2end.helpers.components.node.add_node_menu import AddNode_Menu
from tests.end2end.helpers.constants import NBSP
from tests.end2end.helpers.screens.document.form_edit_included_document import (
    Form_EditIncludedDocument,
)
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)


class Node:  # pylint: disable=invalid-name
    """Base class for DocumentRoot, Section, Requirement"""

    def __init__(self, test_case: BaseCase, node_xpath: str) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_xpath, str)
        self.test_case: BaseCase = test_case
        self.node_xpath: str = node_xpath

    @staticmethod
    def create_from_node_number(test_case: BaseCase, node_order: int = 2):
        xpath = f"(//sdoc-node)[{node_order}]"
        return Node(test_case=test_case, node_xpath=xpath)

    def assert_node_is_editable(self) -> None:
        """
        It makes sense for section & requirements nodes.
        Should have the attribute and the menu button (may be invisible).

        The root node has its own method from DocumentRoot(Node):
        assert_root_node_is_editable().
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
            f"{self.node_xpath}//*[@data-testid='node-edit-action']",
            by=By.XPATH,
        )

    def assert_node_is_not_editable(self) -> None:
        """
        It makes sense for section & requirements nodes (due to 'testid').
        Should not have the menu button (might be invisible).
        """
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}//*[@data-testid='node-edit-action']",
            by=By.XPATH,
        )

    def assert_node_is_deletable(self) -> None:
        """
        It makes sense for section & requirements nodes.
        Should have the menu delete button (may be invisible).
        """
        self.test_case.assert_element_present(
            f"{self.node_xpath}//*[@data-testid='node-delete-action']",
            by=By.XPATH,
        )

    def assert_node_is_not_deletable(self) -> None:
        """
        It makes sense for all nodes.
        Should not have the menu delete button (may be invisible).
        """
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}//*[@data-testid='node-delete-action']",
            by=By.XPATH,
        )

    def assert_node_has_menu(self) -> None:
        """
        It makes sense for all nodes.
        Should have the menu add button (may be invisible).
        """
        self.test_case.assert_element_present(
            f"{self.node_xpath}//*[@data-testid='node-menu-handler']",
            by=By.XPATH,
        )

    def assert_node_has_not_menu(self) -> None:
        """
        It makes sense for all nodes.
        Should not have the menu add button (may be invisible).
        """
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}//*[@data-testid='node-menu-handler']",
            by=By.XPATH,
        )

    def assert_node_does_not_contain(self, text: str) -> None:
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}//*[contains(., '{text}')]",
            by=By.XPATH,
        )

    # Node delete

    def _get_node_delete_confirm(self) -> Confirm:
        """
        Need to be confirmed. For full confirmed action, use do_delete_node.

        Returns:
            Confirm.
        """
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f"{self.node_xpath}//*[@data-testid='node-delete-action']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        # Confirmation required
        return Confirm(self.test_case)

    def do_delete_node(self, proceed_with_confirm: bool = True) -> None:
        confirm = self._get_node_delete_confirm()
        confirm.assert_confirm()
        if proceed_with_confirm:
            confirm.do_confirm_action()

    # Node actions

    def do_open_node_menu(self) -> AddNode_Menu:
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f"{self.node_xpath}//*[@data-testid='node-menu-handler']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return AddNode_Menu(self.test_case, self.node_xpath)

    # forms

    def _do_node_edit(self) -> None:
        """Just click on the edit button"""
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f'{self.node_xpath}//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

    def do_open_form_edit_requirement(self) -> Form_EditRequirement:
        self._do_node_edit()
        self.test_case.assert_element(
            "//sdoc-form",
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_open_form_edit_section(self) -> Form_EditSection:
        self._do_node_edit()
        return Form_EditSection(self.test_case)

    def do_open_form_edit_included_document(self) -> Form_EditIncludedDocument:
        self._do_node_edit()
        return Form_EditIncludedDocument(self.test_case)

    #
    # Title string pattern.
    #
    def create_node_title_string(
        self,
        node_title: str,
        node_level: str = "",
    ) -> str:
        """
        Title pattern: "1.2.3.&nbsp:Title".

        To check in numbered nodes: sections and requirements.

        Args:
            node_title (str): "Title"
            node_level (str, optional): pattern: "1.2.3" (data_level in HTML).
            Defaults to "": then don't check.
        """
        prefix = "" if node_level == "" else f"{node_level}.{NBSP}"
        return f"{prefix}{node_title}"
