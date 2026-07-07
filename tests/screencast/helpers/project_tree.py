from __future__ import annotations

from playwright.sync_api import expect

from tests.screencast.helpers.actions_menu import ActionsMenu
from tests.screencast.helpers.form_add_document import Form_AddDocument
from tests.screencast.helpers.pointer import Pointer


class ProjectTree:
    """
    Playwright counterpart of
    tests/end2end/helpers/screens/project_index/screen_project_index.py,
    covering only what the screencast scenarios currently need.
    """

    def __init__(self, pointer: Pointer) -> None:
        self.pointer = pointer
        self.page = pointer.page
        self.actions_menu = ActionsMenu(pointer)

    def assert_contains_document(self, document_title: str) -> None:
        expect(
            self.page.locator('[data-testid="tree-file-link"]').filter(
                has_text=document_title
            )
        ).to_be_visible()

    def do_open_modal_form_add_document(self) -> Form_AddDocument:
        self.actions_menu.do_click_action("tree-add-document-action")
        expect(self.page.locator("sdoc-modal")).to_be_visible()
        return Form_AddDocument(self.pointer)

    def do_click_on_the_document_with_title(self, document_title: str) -> None:
        link = self.page.locator('[data-testid="tree-file-link"]').filter(
            has_text=document_title
        )
        self.pointer.click(link)
