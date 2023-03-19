from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.add_node_menu import AddNode_Menu
from tests.end2end.helpers.components.confirm import Confirm
from tests.end2end.helpers.constants import NBSP, NODE_0, NODE_1


class Node:  # pylint: disable=invalid-name
    """Base class for DocumentRoot, Section, Requirement"""

    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    def assert_is_node(self, node_order: int = NODE_0) -> None:
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]",
            by=By.XPATH,
        )

    def assert_node_is_editable(
        self,
        node_order: int = NODE_1,
    ) -> None:
        """It makes sense for section & requirements nodes.
        Should have the attribute and the menu button (may be invisible).

        The root node has its own method from DocumentRoot(Node):
        assert_root_node_is_editable().

        Args:
            node_order (int, optional): _description_. Defaults to NODE_1.
        """
        # should have the attribute
        self.test_case.assert_attribute(
            f"(//sdoc-node)[{node_order}]",
            "data-editable_node",
            "on",
            by=By.XPATH,
        )
        # should have the menu button (may be invisible)
        self.test_case.assert_element_present(
            f"(//sdoc-node)[{node_order}]"
            "//*[@data-testid='node-edit-action']",
            by=By.XPATH,
        )

    def assert_node_is_not_editable(
        self,
        node_order: int = NODE_1,
    ) -> None:
        """It makes sense for section & requirements nodes (due to 'testid').
        Should not have the menu button (might be invisible).

        Args:
            node_order (int, optional): _description_. Defaults to NODE_1.
        """
        self.test_case.assert_element_not_present(
            f"(//sdoc-node)[{node_order}]"
            "//*[@data-testid='node-edit-action']",
            by=By.XPATH,
        )

    def assert_node_is_deletable(
        self,
        node_order: int = NODE_1,
    ) -> None:
        """It makes sense for section & requirements nodes.
        Should have the menu delete button (may be invisible).

        Args:
            node_order (int, optional): _description_. Defaults to NODE_1.
        """
        self.test_case.assert_element_present(
            f"(//sdoc-node)[{node_order}]"
            "//*[@data-testid='node-delete-action']",
            by=By.XPATH,
        )

    def assert_node_is_not_deletable(
        self,
        node_order: int = NODE_0,
    ) -> None:
        """It makes sense for all nodes.
        Should not have the menu delete button (may be invisible).

        Args:
            node_order (int, optional): _description_. Defaults to NODE_0.
        """
        self.test_case.assert_element_not_present(
            f"(//sdoc-node)[{node_order}]"
            "//*[@data-testid='node-delete-action']",
            by=By.XPATH,
        )

    def assert_node_has_menu(
        self,
        node_order: int = NODE_0,
    ) -> None:
        """It makes sense for all nodes.
        Should have the menu add button (may be invisible).

        Args:
            node_order (int, optional): _description_. Defaults to NODE_0.
        """
        self.test_case.assert_element_present(
            f"(//sdoc-node)[{node_order}]"
            "//*[@data-testid='node-menu-handler']",
            by=By.XPATH,
        )

    def assert_node_has_not_menu(
        self,
        node_order: int = NODE_0,
    ) -> None:
        """It makes sense for all nodes.
        Should not have the menu add button (may be invisible).

        Args:
            node_order (int, optional): _description_. Defaults to NODE_0.
        """
        self.test_case.assert_element_not_present(
            f"(//sdoc-node)[{node_order}]"
            "//*[@data-testid='node-menu-handler']",
            by=By.XPATH,
        )

    def assert_node_title_contains(
        self,
        node_title: str,
        node_level: str = "",
        node_order: int = NODE_1,
        path: str = "",
    ) -> None:
        """title pattern: "1.2.3.&nbsp:Title".
        To check in numbered nodes: sections and requirements.

        Args:
            node_title (str): "Title"
            node_level (str, optional): pattern: "1.2.3" (data_level in HTML).
            Defaults to "": then don't check.
            node_order (int, optional): _description_. Defaults to NODE_1.
        """
        prefix = "" if node_level == "" else f"{node_level}.{NBSP}"
        self.test_case.assert_element(
            # TODO: improve pattern / testid
            f"(//sdoc-node)[{node_order}]{path}"
            f"//*[contains(., '{prefix}{node_title}')]",
            by=By.XPATH,
        )

    # Node delete

    def do_node_delete_confirm(self, node_order: int = NODE_1) -> Confirm:
        """Need to be confirmed. For full confirmed action, use do_delete_node.

        Args:
            node_order (int, optional): Can't be root node. Defaults to NODE_1.

        Returns:
            Confirm.
        """
        self.test_case.hover_and_click(
            hover_selector=f"(//sdoc-node)[{node_order}]",
            click_selector=(
                f"(//sdoc-node)[{node_order}]"
                "//*[@data-testid='node-delete-action']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        # Confirmation required
        return Confirm(self.test_case)

    def do_delete_node(self, node_order: int = NODE_1) -> None:
        confirm = self.do_node_delete_confirm(node_order)
        confirm.assert_confirm()
        confirm.do_confirm_action()

    # Node actions

    def do_open_node_menu(self, node_order: int = NODE_0) -> AddNode_Menu:
        self.test_case.hover_and_click(
            hover_selector=f"(//sdoc-node)[{node_order}]",
            click_selector=(
                f"(//sdoc-node)[{node_order}]"
                "//*[@data-testid='node-menu-handler']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return AddNode_Menu(self.test_case, node_order)
