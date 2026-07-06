from __future__ import annotations

from playwright.sync_api import Page


class ActionsMenu:
    """
    Playwright counterpart of
    tests/end2end/helpers/components/actions_menu.py, covering only what
    the screencast scenarios currently need.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def do_open(self) -> None:
        self.page.click('[data-testid="header-action-menu-handler"]')

    def do_click_action(self, testid: str) -> None:
        self.do_open()
        self.page.click(f'[data-testid="{testid}"]')
