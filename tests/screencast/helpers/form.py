from __future__ import annotations

from playwright.sync_api import Page, expect


class Form:
    """
    Playwright counterpart of tests/end2end/helpers/form/form.py, covering
    only what the screencast scenarios currently need.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def do_fill_in(self, field_name: str, field_value: str) -> None:
        self.page.locator(f'[data-testid="form-field-{field_name}"]').fill(
            field_value
        )

    def do_form_submit(self) -> None:
        submit_action = self.page.locator('[data-testid="form-submit-action"]')
        submit_action.click()
        expect(submit_action).not_to_be_visible()
