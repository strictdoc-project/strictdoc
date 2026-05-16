from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen

_COLUMNS_BTN = '[data-testid="table-toolbar-columns-btn"]'
_COLUMNS_PANEL = '[data-testid="table-toolbar-columns-panel"]'
_COLUMNS_RESET = '[data-testid="table-toolbar-columns-reset"]'


class Screen_Table(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # overridden for Screen_Table

    def assert_on_screen_table(self) -> None:
        super().assert_on_screen("table")

    # Column visibility toolbar

    def assert_toolbar_btn_label(self, label: str) -> None:
        actual = self.test_case.execute_script(
            f"return document.querySelector('{_COLUMNS_BTN}').textContent"
        )
        assert actual == label, (
            f"Button label: expected {label!r}, got {actual!r}"
        )

    def assert_toolbar_panel_open(self) -> None:
        self.test_case.assert_element_visible(_COLUMNS_PANEL)

    def assert_toolbar_panel_closed(self) -> None:
        self.test_case.assert_element_not_visible(_COLUMNS_PANEL)

    def assert_show_all_disabled(self) -> None:
        disabled = self.test_case.execute_script(
            f"return document.querySelector('{_COLUMNS_RESET}').disabled"
        )
        assert disabled, "Expected Show all button to be disabled"

    def assert_show_all_enabled(self) -> None:
        disabled = self.test_case.execute_script(
            f"return document.querySelector('{_COLUMNS_RESET}').disabled"
        )
        assert not disabled, "Expected Show all button to be enabled"

    def assert_column_header_visible(self, name: str) -> None:
        self.test_case.assert_element_visible(
            f'//th[contains(@class,"content-view-th")][normalize-space()="{name}"]',
            by=By.XPATH,
        )

    def assert_column_header_hidden(self, name: str) -> None:
        self.test_case.assert_element_not_visible(
            f'//th[contains(@class,"content-view-th")][normalize-space()="{name}"]',
            by=By.XPATH,
        )

    def do_open_toolbar_panel(self) -> None:
        self.test_case.click(_COLUMNS_BTN)
        self.assert_toolbar_panel_open()

    def do_toggle_column(self, name: str) -> None:
        self.test_case.click(f'[data-testid="col-checkbox-{name}"]')

    def do_click_show_all(self) -> None:
        self.test_case.click(_COLUMNS_RESET)

    def do_close_panel_by_outside_click(self) -> None:
        self.test_case.click(".content-view-table")
        self.assert_toolbar_panel_closed()
