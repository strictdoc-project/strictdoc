from __future__ import annotations

from playwright.sync_api import expect

from tests.screencast.helpers.pointer import Pointer


class Form:
    """
    Playwright counterpart of tests/end2end/helpers/form/form.py, covering
    only what the screencast scenarios currently need.
    """

    def __init__(self, pointer: Pointer) -> None:
        self.pointer = pointer
        self.page = pointer.page

    def do_fill_in(self, field_name: str, field_value: str) -> None:
        self.pointer.type_into(
            f'[data-testid="form-field-{field_name}"]', field_value
        )

    def do_form_submit(self) -> None:
        submit_action = self.page.locator('[data-testid="form-submit-action"]')
        self.pointer.click('[data-testid="form-submit-action"]')
        expect(submit_action).not_to_be_visible()
