from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen

_COLUMNS_BTN = '[data-testid="table-toolbar-columns-btn"]'
_COLUMNS_BTN_TEXT = _COLUMNS_BTN + " .table-toolbar__btn-text"
_COLUMNS_PANEL = '[data-testid="table-toolbar-columns-panel"]'
_COLUMNS_RESET = '[data-testid="table-toolbar-columns-reset"]'
_ROWS_BTN = '[data-testid="table-toolbar-rows-btn"]'
_ROWS_BTN_TEXT = _ROWS_BTN + " .table-toolbar__btn-text"
_ROWS_PANEL = '[data-testid="table-toolbar-rows-panel"]'
_ROWS_RESET = '[data-testid="table-toolbar-rows-reset"]'
_EDIT_BTN = '[data-testid="table-toolbar-edit-btn"]'


class Screen_Table(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # overridden for Screen_Table

    def assert_on_screen_table(self) -> None:
        super().assert_on_screen("table")

    #
    # Column visibility toolbar
    #

    def assert_toolbar_btn_label(self, label: str) -> None:
        actual = self.test_case.execute_script(
            f"return document.querySelector('{_COLUMNS_BTN_TEXT}').textContent"
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

    #
    # Row visibility toolbar
    #

    def assert_rows_toolbar_btn_label(self, label: str) -> None:
        actual = self.test_case.execute_script(
            f"return document.querySelector('{_ROWS_BTN_TEXT}').textContent"
        )
        assert actual == label, (
            f"Rows button label: expected {label!r}, got {actual!r}"
        )

    def assert_rows_toolbar_panel_open(self) -> None:
        self.test_case.assert_element_visible(_ROWS_PANEL)

    def assert_rows_toolbar_panel_closed(self) -> None:
        self.test_case.assert_element_not_visible(_ROWS_PANEL)

    def assert_rows_show_all_disabled(self) -> None:
        disabled = self.test_case.execute_script(
            f"return document.querySelector('{_ROWS_RESET}').disabled"
        )
        assert disabled, "Expected rows Show all button to be disabled"

    def assert_rows_show_all_enabled(self) -> None:
        disabled = self.test_case.execute_script(
            f"return document.querySelector('{_ROWS_RESET}').disabled"
        )
        assert not disabled, "Expected rows Show all button to be enabled"

    def assert_rows_of_type_visible(self, row_type: str) -> None:
        rows = self.test_case.execute_script(
            f"return Array.from(document.querySelectorAll("
            f"'tr[data-row-type=\"{row_type}\"]')"
            f").every(r => r.style.display !== 'none')"
        )
        assert rows, f"Expected rows of type {row_type!r} to be visible"

    def assert_rows_of_type_hidden(self, row_type: str) -> None:
        rows = self.test_case.execute_script(
            f"return Array.from(document.querySelectorAll("
            f"'tr[data-row-type=\"{row_type}\"]')"
            f").every(r => r.style.display === 'none')"
        )
        assert rows, f"Expected rows of type {row_type!r} to be hidden"

    def do_open_rows_toolbar_panel(self) -> None:
        self.test_case.click(_ROWS_BTN)
        self.assert_rows_toolbar_panel_open()

    def do_toggle_row_type(self, row_type: str) -> None:
        self.test_case.click(f'[data-testid="row-checkbox-{row_type}"]')

    def do_click_rows_show_all(self) -> None:
        self.test_case.click(_ROWS_RESET)

    #
    # Edit mode
    #

    def assert_edit_mode_off(self) -> None:
        pressed = self.test_case.execute_script(
            f"return document.querySelector('{_EDIT_BTN}')"
            f".getAttribute('aria-pressed')"
        )
        assert pressed == "false", (
            f"Expected edit mode OFF (aria-pressed=false), got {pressed!r}"
        )

    def assert_edit_mode_on(self) -> None:
        pressed = self.test_case.execute_script(
            f"return document.querySelector('{_EDIT_BTN}')"
            f".getAttribute('aria-pressed')"
        )
        assert pressed == "true", (
            f"Expected edit mode ON (aria-pressed=true), got {pressed!r}"
        )

    def do_toggle_edit_mode(self) -> None:
        self.test_case.click(_EDIT_BTN)

    def _cell_sel(self, node_mid: str, field_name: str) -> str:
        return f'[data-node-mid="{node_mid}"][data-field-name="{field_name}"]'

    def _input_sel(self, node_mid: str, field_name: str) -> str:
        return self._cell_sel(node_mid, field_name) + " .cell-edit-input"

    def assert_cell_has_validation_error(
        self, node_mid: str, field_name: str
    ) -> None:
        sel = self._cell_sel(node_mid, field_name).replace('"', '\\"')
        has_error = self.test_case.execute_script(
            f'const c = document.querySelector("{sel}");'
            f"return c ? c.getAttribute('data-validation-error') === 'true' : false;"
        )
        assert has_error, (
            f"Expected cell [{node_mid}][{field_name}] to have data-validation-error='true'"
        )

    def assert_cell_has_no_validation_error(
        self, node_mid: str, field_name: str
    ) -> None:
        sel = self._cell_sel(node_mid, field_name).replace('"', '\\"')
        has_error = self.test_case.execute_script(
            f'const c = document.querySelector("{sel}");'
            f"return c ? c.getAttribute('data-validation-error') === 'true' : false;"
        )
        assert not has_error, (
            f"Expected cell [{node_mid}][{field_name}] to have no data-validation-error"
        )

    def assert_no_edit_input(self, node_mid: str, field_name: str) -> None:
        self.test_case.assert_element_not_present(
            self._input_sel(node_mid, field_name)
        )

    def assert_edit_input_visible(self, node_mid: str, field_name: str) -> None:
        self.test_case.assert_element(self._input_sel(node_mid, field_name))

    def assert_cell_value(
        self, node_mid: str, field_name: str, value: str
    ) -> None:
        sel = self._cell_sel(node_mid, field_name).replace('"', '\\"')
        actual = self.test_case.execute_script(
            f'const c = document.querySelector("{sel}");'
            f"return c ? c.dataset.currentValue : null;"
        )
        assert actual == value, (
            f"Cell [{node_mid}][{field_name}]: expected {value!r}, got {actual!r}"
        )

    def assert_cell_text(
        self, node_mid: str, field_name: str, text: str
    ) -> None:
        actual = self.test_case.execute_script(
            f"const c = document.getElementById('cell-{node_mid}-{field_name}');"
            f"return c ? c.textContent.trim() : null;"
        )
        assert actual == text, (
            f"Cell text [{node_mid}][{field_name}]: expected {text!r}, got {actual!r}"
        )

    def do_click_cell(self, node_mid: str, field_name: str) -> None:
        self.test_case.click(self._cell_sel(node_mid, field_name))

    def do_edit_cell_and_submit(
        self, node_mid: str, field_name: str, new_value: str
    ) -> None:
        self.do_click_cell(node_mid, field_name)
        input_sel = self._input_sel(node_mid, field_name)
        self.test_case.assert_element(input_sel)
        self.test_case.type(input_sel, new_value)
        self.test_case.send_keys(input_sel, Keys.RETURN)

    def do_edit_cell_and_cancel(
        self, node_mid: str, field_name: str, new_value: str
    ) -> None:
        self.do_click_cell(node_mid, field_name)
        input_sel = self._input_sel(node_mid, field_name)
        self.test_case.assert_element(input_sel)
        self.test_case.type(input_sel, new_value)
        self.test_case.send_keys(input_sel, Keys.ESCAPE)

    def do_submit_cell_unchanged(self, node_mid: str, field_name: str) -> None:
        self.test_case.send_keys(
            self._input_sel(node_mid, field_name), Keys.RETURN
        )

    #
    # Multiline cell popup
    #

    _MULTILINE_POPUP = "#modal sdoc-modal"
    _MULTILINE_POPUP_CANCEL = '[data-testid="form-cancel-action"]'

    def assert_no_multiline_popup(self) -> None:
        self.test_case.assert_element_not_present(self._MULTILINE_POPUP)

    def assert_multiline_popup_open(self) -> None:
        self.test_case.assert_element_present(self._MULTILINE_POPUP)

    def do_click_multiline_cell(self, node_mid: str, field_name: str) -> None:
        self.test_case.click(self._cell_sel(node_mid, field_name))

    def do_close_multiline_popup_by_btn(self) -> None:
        self.test_case.click(self._MULTILINE_POPUP_CANCEL)
        self.assert_no_multiline_popup()

    def do_close_multiline_popup_by_escape(self) -> None:
        self.test_case.send_keys("body", Keys.ESCAPE)
        self.assert_no_multiline_popup()

    def get_comment_row_mid(self, order: int = 1) -> str:
        xpath = (
            f"(//*[@data-testid='requirement-form-comment-row'])[{order}]"
        )
        element = self.test_case.find_element(xpath, by=By.XPATH)
        mid = element.get_attribute("mid")
        assert mid is not None and len(mid) > 0
        return mid

    def do_submit_multiline_popup(self) -> None:
        self.test_case.click('[data-testid="form-submit-action"]')

    def assert_multiline_popup_has_error(self, message: str) -> None:
        self.test_case.assert_element(
            f'//sdoc-modal//sdoc-form-error[contains(., "{message}")]',
            by=By.XPATH,
        )

    def get_node_mid_from_row(self, row_order: int = 1) -> str:
        return self.test_case.execute_script(
            f"const rows = document.querySelectorAll("
            f"'tr[data-row-type] [data-node-mid]');"
            f"const cell = rows[{row_order - 1}];"
            f"return cell ? cell.dataset.nodeMid : null;"
        )
