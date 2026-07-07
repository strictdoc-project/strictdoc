from __future__ import annotations

from playwright.sync_api import Locator

from tests.screencast.helpers.form_edit_requirement import Form_EditRequirement
from tests.screencast.helpers.pointer import Pointer


class AddNode_Menu:  # noqa: N801
    """
    Playwright counterpart of
    tests/end2end/helpers/components/node/add_node_menu.py, covering only
    what the screencast scenarios currently need.
    """

    def __init__(self, pointer: Pointer, node_locator: Locator) -> None:
        self.pointer = pointer
        self.node_locator = node_locator

    def do_node_add_requirement_first(self) -> Form_EditRequirement:
        self.pointer.click(
            self.node_locator.locator(
                '[data-testid="node-add-requirement-first-action"]'
            )
        )
        return Form_EditRequirement(self.pointer)

    def do_node_add_requirement_below(self) -> Form_EditRequirement:
        self.pointer.click(
            self.node_locator.locator(
                '[data-testid="node-add-requirement-below-action"]'
            )
        )
        return Form_EditRequirement(self.pointer)


class Node:
    """
    Playwright counterpart of
    tests/end2end/helpers/components/node/node.py, covering only what the
    screencast scenarios currently need.
    """

    def __init__(self, pointer: Pointer, node_locator: Locator) -> None:
        self.pointer = pointer
        self.node_locator = node_locator

    def do_open_node_menu(self) -> AddNode_Menu:
        self.pointer.move_to(self.node_locator)
        self.pointer.click(
            self.node_locator.locator('[data-testid="node-menu-handler"]')
        )
        return AddNode_Menu(self.pointer, self.node_locator)


class DocumentRoot(Node):
    def __init__(self, pointer: Pointer) -> None:
        super().__init__(
            pointer, pointer.page.locator('[data-testid="node-root"]')
        )


class Requirement(Node):
    @staticmethod
    def with_node(pointer: Pointer, node_order: int = 1) -> "Requirement":
        locator = pointer.page.locator(
            '[data-testid="node-requirement"]'
        ).nth(node_order - 1)
        return Requirement(pointer, locator)
