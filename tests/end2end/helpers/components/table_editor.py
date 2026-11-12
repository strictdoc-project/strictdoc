from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from tests.end2end.helpers.components.field_widgets import FieldWidgets


class TableEditor(FieldWidgets):  # pylint: disable=invalid-name
    """
    The table editor of a multiline form field: the table highlights, the
    field's button in table mode, and the editor modal.
    """

    MODAL = "//*[@data-testid='table-editor-modal']"

    # field

    def assert_highlighted_tables(self, count: int) -> None:
        actual = self.test_case.execute_script(
            "return CSS.highlights.get('sdoc-table')?.size ?? 0;"
        )
        assert actual == count, f"{actual} != {count}"

    def wait_for_highlighted_tables(
        self, count: int, timeout: float = 5
    ) -> None:
        """
        The table view loads an inline form asynchronously. Wait until
        StrictDoc.onInsert() initializes the table editor for that form.
        """
        WebDriverWait(self.test_case.driver, timeout).until(
            lambda _: (
                self.test_case.execute_script(
                    "return CSS.highlights.get('sdoc-table')?.size ?? 0;"
                )
                == count
            )
        )

    # button

    def do_open_insert(self) -> None:
        """
        Opens the editor with a new 3 x 3 table, a header and 2 rows, through
        the insert menu.
        """
        self.do_open_insert_menu()
        self.do_choose_insert_item("table")
        self.assert_open()

    def do_open_edit(self) -> None:
        self.assert_button("edit")
        self.test_case.click_xpath(self.button_xpath)
        self.assert_open()

    # modal

    def assert_open(self) -> None:
        self.test_case.assert_element(self.MODAL, by=By.XPATH)

    def assert_not_open(self) -> None:
        self.test_case.assert_element_not_present(self.MODAL, by=By.XPATH)

    def _cell_xpath(self, row: int, column: int) -> str:
        return (
            f"{self.MODAL}//*[@data-testid='table-editor-cell' and "
            f"@data-row='{row}' and "
            f"@data-column='{column}']"
        )

    def assert_cell(self, row: int, column: int, value: str) -> None:
        cell = self.test_case.find_element(
            self._cell_xpath(row, column), by=By.XPATH
        )
        actual = self.test_case.execute_script(
            "return arguments[0].innerText;", cell
        )
        assert actual == value, f"{actual!r} != {value!r}"

    def do_fill_cell(self, row: int, column: int, value: str) -> None:
        r"""
        Row 0 is the header row. A "\n" in `value` presses Enter.
        """
        self.test_case.type(self._cell_xpath(row, column), value, by=By.XPATH)

    def _grip_xpath(self, target: str, index: int) -> str:
        return (
            f"{self.MODAL}//*[@data-testid='table-editor-{target}-grip'"
            f" and @data-{target}='{index}']"
        )

    def do_insert_column(self, at: int) -> None:
        """Clicks the "+" that inserts a column at `at`."""
        self.test_case.click_xpath(
            f"{self.MODAL}//*[@data-testid='table-editor-insert-column'"
            f" and @data-column='{at}']"
        )

    def do_menu_action(self, target: str, index: int, action: str) -> None:
        """
        Clicks the grip of a body row or a column and an item of its menu:
        insert-above, insert-below, insert-left, insert-right, delete.
        """
        self.test_case.click_xpath(self._grip_xpath(target, index))
        self.test_case.click_xpath(
            f"{self.MODAL}//*[@data-testid='table-editor-menu-{action}']"
        )

    def do_delete_row(self, row: int) -> None:
        self.do_menu_action("row", row, "delete")

    def do_click_extend(self, target: str) -> None:
        """Clicks the bar below ("row") or right of ("column") the table."""
        self.test_case.click_xpath(
            f"{self.MODAL}//*[@data-testid='table-editor-extend-{target}s']"
        )

    def do_drag_extend(self, target: str, steps: int) -> None:
        """
        Drags the bar below ("row") or right of ("column") the table by
        `steps` sizes of the last row or column; a negative count removes
        empty ones.
        """
        bar = self.test_case.find_element(
            f"{self.MODAL}//*[@data-testid='table-editor-extend-{target}s']",
            by=By.XPATH,
        )
        # The table cell (th or td) of the last column or row.
        cells = (
            f"{self.MODAL}//*[@data-testid='table-editor-cell' and "
            "@data-row='0']/.."
            if target == "column"
            else f"{self.MODAL}//*[@data-testid='table-editor-cell']/.."
        )
        last = self.test_case.find_elements(cells, by=By.XPATH)[-1]
        if target == "row":
            offset = (0, steps * last.size["height"])
        else:
            offset = (steps * last.size["width"], 0)
        ActionChains(self.test_case.driver).click_and_hold(bar).move_by_offset(
            *offset
        ).release().perform()

    def _do_drag(self, target: str, index: int, before: int) -> None:
        """
        Drags the grip of row or column `index` and drops it before the
        row or column `before` (the header row is row 0), or after the last
        one if `before` is the count.
        """
        source = self.test_case.find_element(
            self._grip_xpath(target, index), by=By.XPATH
        )
        cells = (
            f"{self.MODAL}//*[@data-testid='table-editor-cell' and "
            f"@data-{target}='{{}}']"
        )
        count = len(
            self.test_case.find_elements(
                f"{self.MODAL}//*[@data-testid='table-editor-cell' and "
                f"@data-{'column' if target == 'row' else 'row'}='0']",
                by=By.XPATH,
            )
        )
        is_after = before == count
        target_cell = self.test_case.find_element(
            cells.format(before - 1 if is_after else before), by=By.XPATH
        )
        size = target_cell.size
        # Offsets are from the center: a quarter towards the edge to drop at.
        sign = 1 if is_after else -1
        x_offset = sign * size["width"] // 4 if target == "column" else 0
        y_offset = sign * size["height"] // 4 if target == "row" else 0
        ActionChains(self.test_case.driver).click_and_hold(
            source
        ).move_by_offset(5, 5).move_to_element_with_offset(
            target_cell, x_offset, y_offset
        ).release().perform()

    def do_drag_row(self, row: int, before: int) -> None:
        self._do_drag("row", row, before)

    def do_drag_column(self, column: int, before: int) -> None:
        self._do_drag("column", column, before)

    def do_apply(self) -> None:
        self.test_case.click_xpath(
            f"{self.MODAL}//*[@data-testid='table-editor-apply-action']"
        )
        self.assert_not_open()

    def do_cancel(self) -> None:
        self.test_case.click_xpath(
            f"{self.MODAL}//*[@data-testid='table-editor-cancel-action']"
        )
        self.assert_not_open()

    def do_close_by_escape(self) -> None:
        """Presses Escape in the focused editor cell."""
        ActionChains(self.test_case.driver).send_keys(Keys.ESCAPE).perform()
        self.assert_not_open()
