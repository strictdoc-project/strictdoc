from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.screencast.helpers.screen import Screen


class ViewTypeSelector:
    """
    Playwright counterpart of
    tests/end2end/helpers/components/viewtype_selector.py, covering only
    what the screencast scenarios currently need.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def go_to_table(self) -> Screen:
        self.page.click("#viewtype_handler")

        table_link = self.page.locator('[data-viewtype_link="table"]')
        expect(table_link).to_be_visible()
        table_link.click()

        return Screen(self.page)
