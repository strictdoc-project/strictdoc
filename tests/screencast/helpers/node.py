from __future__ import annotations

from playwright.sync_api import Page

from tests.screencast.helpers.form_edit_requirement import Form_EditRequirement


class AddNode_Menu:  # noqa: N801
    """
    Playwright counterpart of
    tests/end2end/helpers/components/node/add_node_menu.py, covering only
    what the screencast scenarios currently need.
    """

    def __init__(self, page: Page, node_selector: str) -> None:
        self.page = page
        self.node_selector = node_selector

    def do_node_add_requirement_first(self) -> Form_EditRequirement:
        self.page.click(
            f'{self.node_selector} [data-testid="node-add-requirement-first-action"]'
        )
        return Form_EditRequirement(self.page)


class Node:
    """
    Playwright counterpart of
    tests/end2end/helpers/components/node/node.py, covering only what the
    screencast scenarios currently need.
    """

    def __init__(self, page: Page, node_selector: str) -> None:
        self.page = page
        self.node_selector = node_selector

    def do_open_node_menu(self) -> AddNode_Menu:
        self.page.hover(self.node_selector)
        self.page.click(
            f'{self.node_selector} [data-testid="node-menu-handler"]'
        )
        return AddNode_Menu(self.page, self.node_selector)


class DocumentRoot(Node):
    def __init__(self, page: Page) -> None:
        super().__init__(page, '[data-testid="node-root"]')
