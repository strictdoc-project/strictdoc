from __future__ import annotations

from tests.screencast.helpers.pointer import Pointer


class ActionsMenu:
    """
    Playwright counterpart of
    tests/end2end/helpers/components/actions_menu.py, covering only what
    the screencast scenarios currently need.
    """

    def __init__(self, pointer: Pointer) -> None:
        self.pointer = pointer

    def do_open(self) -> None:
        self.pointer.click('[data-testid="header-action-menu-handler"]')

    def do_click_action(self, testid: str) -> None:
        self.do_open()
        self.pointer.click(f'[data-testid="{testid}"]')
