from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.screen import Screen

_SORT_RESET_BTN = '[data-testid="table-toolbar-sort-reset"]'
_SORT_RESET_WRAPPER = ".table-toolbar__sort-reset"
_COLUMNS_BTN = '[data-testid="table-toolbar-columns-btn"]'
_COLUMNS_BTN_TEXT = _COLUMNS_BTN + " .table-toolbar__btn-text"
_COLUMNS_BTN_INFO = _COLUMNS_BTN + " .table-toolbar__btn-info"
_COLUMNS_PANEL = '[data-testid="table-toolbar-columns-panel"]'
_COLUMNS_RESET = '[data-testid="table-toolbar-columns-reset"]'
_ROWS_BTN = '[data-testid="table-toolbar-rows-btn"]'
_ROWS_BTN_TEXT = _ROWS_BTN + " .table-toolbar__btn-text"
_ROWS_BTN_INFO = _ROWS_BTN + " .table-toolbar__btn-info"
_ROWS_PANEL = '[data-testid="table-toolbar-rows-panel"]'
_ROWS_RESET = '[data-testid="table-toolbar-rows-reset"]'
_EDIT_BTN = '[data-testid="table-toolbar-edit-btn"]'
_ADD_ROW = '[data-testid="table-add-row"]'


class Screen_Table(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    # overridden for Screen_Table

    def assert_on_screen_table(self) -> None:
        super().assert_on_screen("table")

    #
    # Column sorting
    #

    def do_click_col_sort_btn(self, col_name: str) -> None:
        self.test_case.click(
            f'[data-testid="col-header-{col_name}"] .content-view-th__sort-btn'
        )

    def do_click_col_sort_btn_without_scrolling(self, col_name: str) -> None:
        self.test_case.execute_script(
            """
            document.querySelector(
              `[data-testid="col-header-${arguments[0]}"] `
              + '.content-view-th__sort-btn'
            )?.click();
            """,
            col_name,
        )

    def assert_col_sort_state(self, col_name: str, state) -> None:
        # state: 'asc', 'desc', or None (unsorted)
        element = self.test_case.find_element(
            f'[data-testid="col-header-{col_name}"]'
        )
        actual = element.get_attribute("data-sort")
        assert actual == state, (
            f"Column {col_name!r} sort state: expected {state!r}, got {actual!r}"
        )

    def assert_sort_reset_hidden(self) -> None:
        # Use execute_script to read the hidden attribute without waiting for visibility.
        is_hidden = self.test_case.execute_script(
            "const el = document.querySelector('.table-toolbar__sort-reset');"
            "return el ? el.hasAttribute('hidden') : true;"
        )
        assert is_hidden, "Expected sort reset button to be hidden"

    def assert_sort_reset_visible(self) -> None:
        is_hidden = self.test_case.execute_script(
            "const el = document.querySelector('.table-toolbar__sort-reset');"
            "return el ? el.hasAttribute('hidden') : true;"
        )
        assert not is_hidden, "Expected sort reset button to be visible"

    def do_click_sort_reset(self) -> None:
        self.test_case.click(_SORT_RESET_BTN)

    def get_nth_row_field_text(self, row_index: int, field_name: str) -> str:
        # row_index is 1-based; reads textContent of the matching field cell.
        return self.test_case.execute_script(
            "const rows = Array.from("
            "  document.querySelectorAll('.content-view-table tbody tr[data-row-type]')"
            ");"
            f"const row = rows[{row_index - 1}];"
            "if (!row) return null;"
            f"const cell = row.querySelector('[data-field-name=\"{field_name}\"]');"
            "return cell ? cell.textContent.trim() : null;"
        )

    def do_reload_with_hidden_columns(self, hidden: str) -> None:
        current_url = self.test_case.get_current_url()
        # Strip both query string and hash fragment before appending new params.
        base_url = current_url.split("?")[0].split("#")[0]
        self.test_case.open(f"{base_url}?hidden={hidden}")
        self.assert_on_screen_table()

    #
    # Column visibility toolbar
    #

    def assert_toolbar_btn_label(self, label: str) -> None:
        actual = self.test_case.get_text(_COLUMNS_BTN_TEXT)
        assert actual == label, (
            f"Columns btn label: expected {label!r}, got {actual!r}"
        )

    def assert_toolbar_panel_open(self) -> None:
        self.test_case.assert_element_visible(_COLUMNS_PANEL)

    def assert_toolbar_panel_closed(self) -> None:
        self.test_case.assert_element_not_visible(_COLUMNS_PANEL)

    def assert_show_all_disabled(self) -> None:
        element = self.test_case.find_element(_COLUMNS_RESET)
        assert not element.is_enabled(), (
            "Expected Show all button to be disabled"
        )

    def assert_show_all_enabled(self) -> None:
        element = self.test_case.find_element(_COLUMNS_RESET)
        assert element.is_enabled(), "Expected Show all button to be enabled"

    def assert_column_header_visible(self, name: str) -> None:
        self.test_case.assert_element_visible(
            f'[data-testid="col-header-{name}"]'
        )

    def assert_column_header_hidden(self, name: str) -> None:
        self.test_case.assert_element_not_visible(
            f'[data-testid="col-header-{name}"]'
        )

    def assert_column_cells_hidden(self, name: str) -> None:
        cells_are_hidden = self.test_case.execute_script(
            "const table = document.querySelector('.content-view-table');"
            "const headers = Array.from("
            "  table.querySelectorAll(':scope > thead > tr > th')"
            ");"
            f"const header = table.querySelector('[data-testid=\"col-header-{name}\"]');"
            "const index = headers.indexOf(header);"
            "if (index < 0) return false;"
            "return Array.from("
            "  table.querySelectorAll(':scope > tbody > tr[data-row-type]')"
            ").every(row => {"
            "  const cell = row.children[index];"
            "  return !cell || getComputedStyle(cell).display === 'none';"
            "});"
        )
        assert cells_are_hidden, (
            f"Expected all cells in column {name!r} to be hidden"
        )

    def assert_column_header_not_present(self, name: str) -> None:
        self.test_case.assert_element_not_present(
            f'[data-testid="col-header-{name}"]'
        )

    def assert_table_cell_is_dimmed(
        self, row_type: str, field_name: str
    ) -> None:
        self.test_case.assert_element(
            f'//tr[@data-row-type="{row_type}"]'
            f'//td[@data-field-name="{field_name}"]'
            f'[contains(@class,"content-view-td--dimmed")]',
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
        actual = self.test_case.get_text(_ROWS_BTN_TEXT)
        assert actual == label, (
            f"Rows btn label: expected {label!r}, got {actual!r}"
        )

    def assert_rows_toolbar_panel_open(self) -> None:
        self.test_case.assert_element_visible(_ROWS_PANEL)

    def assert_rows_toolbar_panel_closed(self) -> None:
        self.test_case.assert_element_not_visible(_ROWS_PANEL)

    def assert_rows_show_all_disabled(self) -> None:
        element = self.test_case.find_element(_ROWS_RESET)
        assert not element.is_enabled(), (
            "Expected rows Show all button to be disabled"
        )

    def assert_rows_show_all_enabled(self) -> None:
        element = self.test_case.find_element(_ROWS_RESET)
        assert element.is_enabled(), (
            "Expected rows Show all button to be enabled"
        )

    def assert_rows_of_type_visible(self, row_type: str) -> None:
        rows = self.test_case.find_elements(f'tr[data-row-type="{row_type}"]')
        for row in rows:
            assert row.is_displayed(), (
                f"Expected rows of type {row_type!r} to be visible"
            )

    def assert_rows_of_type_hidden(self, row_type: str) -> None:
        rows = self.test_case.find_elements(f'tr[data-row-type="{row_type}"]')
        for row in rows:
            assert not row.is_displayed(), (
                f"Expected rows of type {row_type!r} to be hidden"
            )

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
        element = self.test_case.find_element(_EDIT_BTN)
        pressed = element.get_attribute("aria-pressed")
        assert pressed == "false", (
            f"Expected edit mode OFF (aria-pressed=false), got {pressed!r}"
        )

    def assert_edit_mode_on(self) -> None:
        element = self.test_case.find_element(_EDIT_BTN)
        pressed = element.get_attribute("aria-pressed")
        assert pressed == "true", (
            f"Expected edit mode ON (aria-pressed=true), got {pressed!r}"
        )

    def do_toggle_edit_mode(self) -> None:
        self.test_case.click(_EDIT_BTN)

    def get_table_row_count(self) -> int:
        return len(
            self.test_case.find_elements(
                ".content-view-table tbody tr[data-row-type]"
            )
        )

    def do_open_add_node_menu(self, row_order: int = 1) -> None:
        # The handle is a full-width but near-zero-height row. After a sort
        # reset the table rows are reordered while the page scroll position
        # stays put, so this handle can end up positioned behind the sticky
        # table header (same z-index situation as do_click_add_node_action).
        # A native click() would then hit the header instead, so dispatch
        # the click via JS to bypass the visibility/interception check.
        handle = self.test_case.find_element(
            f"(//*[@data-testid='table-add-node-handle'])[{row_order}]",
            by=By.XPATH,
        )
        self.test_case.execute_script("arguments[0].click();", handle)
        self.test_case.wait_for_element(
            f"(//*[@data-testid='table-add-row'])[{row_order}]"
            "//*[@data-testid='table-add-node-menu' and not(@hidden)]",
            by=By.XPATH,
            timeout=3,
        )

    def assert_add_node_action_disabled(
        self, element_type: str, whereto: str, row_order: int = 1
    ) -> None:
        self.test_case.assert_element(
            f"(//*[@data-testid='table-add-row'])[{row_order}]"
            f"//*[@data-testid='table-add-node-action-{element_type.lower()}-{whereto}' and @disabled]",
            by=By.XPATH,
        )

    def assert_add_node_message(
        self, message: str, row_order: int | None = 1
    ) -> None:
        add_node = (
            f"(//*[@data-testid='table-add-row'])[{row_order}]"
            if row_order is not None
            else "//*[@js-table_view_edit-add-node and @data-mode='open']"
        )
        self.test_case.assert_element(
            add_node
            + f"//*[contains(@class, 'table-add-node__message')][contains(., '{message}')]",
            by=By.XPATH,
        )

    def assert_add_node_actions_hidden(
        self, row_order: int | None = 1
    ) -> None:
        add_node = (
            f"(//*[@data-testid='table-add-row'])[{row_order}]"
            if row_order is not None
            else "//*[@js-table_view_edit-add-node and @data-mode='open']"
        )
        self.test_case.assert_element_not_visible(
            add_node + "//*[@js-table_view_edit-add-node-actions]",
            by=By.XPATH,
        )

    def assert_add_node_actions_visible(
        self, row_order: int | None = 1
    ) -> None:
        add_node = (
            f"(//*[@data-testid='table-add-row'])[{row_order}]"
            if row_order is not None
            else "//*[@js-table_view_edit-add-node and @data-mode='open']"
        )
        self.test_case.assert_element_visible(
            add_node + "//*[@js-table_view_edit-add-node-actions]",
            by=By.XPATH,
        )

    def do_click_add_node_unblock(
        self, blocker: str, row_order: int | None = 1
    ) -> None:
        add_node = (
            f"(//*[@data-testid='table-add-row'])[{row_order}]"
            if row_order is not None
            else "//*[@js-table_view_edit-add-node and @data-mode='open']"
        )
        self.test_case.click(
            add_node
            + f"//*[@data-testid='table-add-node-unblock-{blocker}']",
            by=By.XPATH,
        )
        self.test_case.sleep(0.1)

    def do_close_add_node_menu_by_escape(self) -> None:
        self.test_case.send_keys("body", Keys.ESCAPE)

    def do_click_add_node_action(
        self, element_type: str, whereto: str, row_order: int = 1
    ) -> None:
        action = self.test_case.find_element(
            f"(//*[@data-testid='table-add-row'])[{row_order}]"
            f"//*[@data-testid='table-add-node-action-{element_type.lower()}-{whereto}']",
            by=By.XPATH,
        )
        self.test_case.execute_script("arguments[0].click();", action)

    def get_open_add_node_menu_viewport_position(self) -> dict:
        position = self.test_case.execute_script(
            """
            const menu = document.querySelector(
              '[js-table_view_edit-add-node][data-mode="open"] '
              + '[js-table_view_edit-add-node-menu]'
            );
            if (!menu) return null;
            const bounds = menu.getBoundingClientRect();
            return {left: bounds.left, top: bounds.top};
            """
        )
        assert position is not None, "Expected an open Add Node menu"
        return position

    def scroll_open_add_node_menu_to_center(self) -> None:
        self.test_case.execute_script(
            """
            const menu = document.querySelector(
              '[js-table_view_edit-add-node][data-mode="open"] '
              + '[js-table_view_edit-add-node-menu]'
            );
            const main = menu?.closest('.main');
            if (!menu || !main) return;
            const scrollBehavior = main.style.scrollBehavior;
            main.style.scrollBehavior = 'auto';
            menu.scrollIntoView({block: 'center'});
            main.style.scrollBehavior = scrollBehavior;
            """
        )

    def scroll_node_row_to_center(self, node_mid: str) -> None:
        self.test_case.execute_script(
            """
            const row = document.querySelector(
              `tr[data-node-mid="${arguments[0]}"]`
            );
            const main = row?.closest('.main');
            if (!row || !main) return;
            const scrollBehavior = main.style.scrollBehavior;
            main.style.scrollBehavior = 'auto';
            row.scrollIntoView({block: 'center'});
            main.style.scrollBehavior = scrollBehavior;
            """,
            node_mid,
        )

    def get_node_row_viewport_position(self, node_mid: str) -> dict:
        position = self.test_case.execute_script(
            """
            const row = document.querySelector(
              `tr[data-node-mid="${arguments[0]}"]`
            );
            if (!row) return null;
            const bounds = row.getBoundingClientRect();
            return {left: bounds.left, top: bounds.top};
            """,
            node_mid,
        )
        assert position is not None, f"Expected row for node MID {node_mid!r}"
        return position

    def assert_add_rows_not_present(self) -> None:
        self.test_case.assert_element_not_present(_ADD_ROW)

    def _cell_sel(self, node_mid: str, field_name: str) -> str:
        return f'[data-node-mid="{node_mid}"][data-field-name="{field_name}"]'

    def assert_cell_has_validation_error(
        self, node_mid: str, field_name: str
    ) -> None:
        sel = self._cell_sel(node_mid, field_name)
        element = self.test_case.find_element(sel)
        has_error = element.get_attribute("data-validation-error") == "true"
        assert has_error, (
            f"Expected cell [{node_mid}][{field_name}] to have data-validation-error='true'"
        )

    def assert_cell_has_no_validation_error(
        self, node_mid: str, field_name: str
    ) -> None:
        sel = self._cell_sel(node_mid, field_name)
        element = self.test_case.find_element(sel)
        has_error = element.get_attribute("data-validation-error") == "true"
        assert not has_error, (
            f"Expected cell [{node_mid}][{field_name}] to have no data-validation-error"
        )

    def assert_cell_dom_text(
        self, node_mid: str, field_name: str, text: str
    ) -> None:
        # Verifies that the specific cell's DOM was updated (not just that the text
        # exists somewhere on the page). Uses textContent instead of get_text()
        # because the display div inside autocomplete cells is hidden.
        actual = self.test_case.execute_script(
            f"const c = document.getElementById('cell-{node_mid}-{field_name}');"
            f"return c ? c.textContent.trim() : null;"
        )
        assert actual == text, (
            f"Cell DOM text [{node_mid}][{field_name}]: expected {text!r}, got {actual!r}"
        )

    def assert_cell_dom_text_contains(
        self, node_mid: str, field_name: str, text: str
    ) -> None:
        # textContent (not get_text()/assert_text()) so the check doesn't
        # depend on the cell being scrolled into view in this wide table,
        # and doesn't depend on the exact whitespace of the rendered markup.
        actual = self.test_case.execute_script(
            f"const c = document.getElementById('cell-{node_mid}-{field_name}');"
            f"return c ? c.textContent.trim() : null;"
        )
        assert actual is not None and text in actual, (
            f"Cell DOM text [{node_mid}][{field_name}]: expected to contain {text!r}, got {actual!r}"
        )

    def assert_cell_dom_text_not_contains(
        self, node_mid: str, field_name: str, text: str
    ) -> None:
        # See assert_cell_dom_text_contains for why textContent is used here.
        actual = self.test_case.execute_script(
            f"const c = document.getElementById('cell-{node_mid}-{field_name}');"
            f"return c ? c.textContent.trim() : null;"
        )
        assert actual is not None and text not in actual, (
            f"Cell DOM text [{node_mid}][{field_name}]: expected NOT to contain {text!r}, got {actual!r}"
        )

    def do_click_cell(self, node_mid: str, field_name: str) -> None:
        self.test_case.click(self._cell_sel(node_mid, field_name))

    #
    # Inline cell forms (comments, relations, multiline, singleline, autocomplete)
    #

    def assert_cell_is_inline_editing(
        self, node_mid: str, field_name: str
    ) -> None:
        sel = self._cell_sel(node_mid, field_name)
        element = self.test_case.find_element(sel)
        mode = element.get_attribute("data-mode") or ""
        assert mode == "editing", (
            f"Expected cell [{node_mid}][{field_name}] to have data-mode='editing', got {mode!r}"
        )

    def assert_cell_is_not_inline_editing(
        self, node_mid: str, field_name: str
    ) -> None:
        sel = self._cell_sel(node_mid, field_name)
        element = self.test_case.find_element(sel)
        mode = element.get_attribute("data-mode") or ""
        assert mode != "editing", (
            f"Expected cell [{node_mid}][{field_name}] NOT to have data-mode='editing'"
        )

    def do_open_inline_cell(self, node_mid: str, field_name: str) -> None:
        self.test_case.click(self._cell_sel(node_mid, field_name))
        self.assert_cell_is_inline_editing(node_mid, field_name)

    def do_save_inline_cell_by_outside_click(self) -> None:
        # Click the page header: always visible regardless of horizontal scroll.
        self.test_case.click("#header-project-name")

    def do_cancel_inline_cell_by_escape(self) -> None:
        self.test_case.send_keys("body", Keys.ESCAPE)

    def do_save_inline_cell_by_cmd_enter(self) -> None:
        ActionChains(self.test_case.driver).key_down(Keys.CONTROL).send_keys(
            Keys.RETURN
        ).key_up(Keys.CONTROL).perform()

    def get_comment_row_mid(self, order: int = 1) -> str:
        xpath = f"(//*[@data-testid='requirement-form-comment-row'])[{order}]"
        element = self.test_case.find_element(xpath, by=By.XPATH)
        mid = element.get_attribute("mid")
        assert mid is not None and len(mid) > 0
        return mid

    def do_cell_autocomplete(
        self, node_mid: str, field_name: str, field_value: str
    ) -> None:
        # Click the cell to trigger openAutocompleteCell — turbo-stream injects
        # the sdoc-autocompletable form into the cell div.
        self.test_case.click(self._cell_sel(node_mid, field_name))
        field_xpath = f"(//*[@data-testid='form-field-{field_name}'])"
        self.test_case.wait_for_element(field_xpath, by=By.XPATH, timeout=3)
        element = self.test_case.find_element(field_xpath, by=By.XPATH)
        hidden_input = element.find_element(
            By.XPATH, "following-sibling::input[@type='hidden']"
        )
        results_ul = hidden_input.find_element(
            By.XPATH, "following-sibling::ul[1]"
        )
        self.test_case.type(field_xpath, field_value, by=By.XPATH)
        WebDriverWait(self.test_case.driver, 3).until(
            lambda _: results_ul.is_displayed()
        )
        len_before = len(element.text.lower().strip())
        ActionChains(self.test_case.driver).send_keys(Keys.ARROW_DOWN).pause(
            0.1
        ).send_keys(Keys.RETURN).perform()
        WebDriverWait(self.test_case.driver, 3).until(
            lambda _: len(element.text.lower().strip()) > len_before
        )

    def do_cell_autocomplete_again(
        self, field_name: str, field_value: str
    ) -> None:
        # Cell is already open; find the injected sdoc-autocompletable by testid.
        field_xpath = f"(//*[@data-testid='form-field-{field_name}'])"
        element = self.test_case.find_element(field_xpath, by=By.XPATH)
        hidden_input = element.find_element(
            By.XPATH, "following-sibling::input[@type='hidden']"
        )
        results_ul = hidden_input.find_element(
            By.XPATH, "following-sibling::ul[1]"
        )
        element.send_keys(f",{field_value}")
        WebDriverWait(self.test_case.driver, 3).until(
            lambda _: results_ul.is_displayed()
        )
        len_before = len(element.text.lower().strip())
        ActionChains(self.test_case.driver).send_keys(Keys.ARROW_DOWN).pause(
            0.1
        ).send_keys(Keys.RETURN).perform()
        WebDriverWait(self.test_case.driver, 3).until(
            lambda _: len(element.text.lower().strip()) > len_before
        )

    def do_submit_cell_autocomplete(self) -> None:
        # Click the table header to move focus away from the cell and trigger blur → save
        self.test_case.click(".content-view-table thead th")

    def get_node_mid_from_row(self, row_order: int = 1) -> str:
        row = self.test_case.find_element(
            f"(//tr[@data-row-type])[{row_order}]", by=By.XPATH
        )
        return row.get_attribute("data-node-mid")

    def assert_delete_action_hidden(self, node_mid: str) -> None:
        self.test_case.assert_element_not_visible(
            f'[data-node-mid="{node_mid}"] '
            '[data-testid="form-delete-action"]'
        )

    def assert_delete_action_visible(self, node_mid: str) -> None:
        self.test_case.assert_element_visible(
            f'[data-node-mid="{node_mid}"] '
            '[data-testid="form-delete-action"]'
        )

    def do_click_delete_action(self, node_mid: str) -> None:
        self.test_case.click(
            f'[data-node-mid="{node_mid}"] '
            '[data-testid="form-delete-action"]'
        )

    def assert_node_row_not_present(self, node_mid: str) -> None:
        self.test_case.assert_element_not_present(
            f'[data-node-mid="{node_mid}"]'
        )
