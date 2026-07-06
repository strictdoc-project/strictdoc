from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.screencast.helpers.actions_menu import ActionsMenu
from tests.screencast.helpers.form_add_document import Form_AddDocument


class ProjectTree:
    """
    Playwright counterpart of
    tests/end2end/helpers/screens/project_index/screen_project_index.py,
    covering only what the screencast scenarios currently need.
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.actions_menu = ActionsMenu(page)

    def assert_contains_document(self, document_title: str) -> None:
        expect(
            self.page.locator('[data-testid="tree-file-link"]').filter(
                has_text=document_title
            )
        ).to_be_visible()

    def do_open_modal_form_add_document(self) -> Form_AddDocument:
        self.actions_menu.do_click_action("tree-add-document-action")
        expect(self.page.locator("sdoc-modal")).to_be_visible()
        return Form_AddDocument(self.page)

    def do_click_on_the_document_with_title(self, document_title: str) -> None:
        self.page.locator('[data-testid="tree-file-link"]').filter(
            has_text=document_title
        ).click()
