from __future__ import annotations

from playwright.sync_api import Page, expect


class Screen:
    """
    Playwright counterpart of tests/end2end/helpers/screens/screen.py,
    covering only what the screencast scenarios currently need.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def assert_on_screen(self, viewtype: str) -> None:
        expect(self.page.locator("body")).to_have_attribute(
            "data-viewtype", viewtype
        )

    def assert_header_document_title(self, title: str) -> None:
        expect(self.page.locator(".header__document_title")).to_contain_text(
            title
        )
