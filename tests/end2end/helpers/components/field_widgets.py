import platform
from typing import List

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import BaseCase


class FieldWidgets:  # pylint: disable=invalid-name
    """
    The field widgets of a multiline form field: the caret, the field's
    button, and the insert menu with its placeholder at the caret.
    """

    INSERT_MENU = "//*[@data-testid='field-widgets-insert-menu']"
    PLACEHOLDER = "//*[@data-testid='field-widgets-placeholder']"

    def __init__(self, test_case: BaseCase, field_name: str) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(field_name, str)
        self.test_case: BaseCase = test_case
        self.field_xpath = f"//*[@data-testid='form-field-{field_name}']"
        self.button_xpath = (
            f"{self.field_xpath}/following-sibling::"
            "*[@data-testid='field-widgets-button']"
        )
        self.extra_button_xpath = (
            f"{self.field_xpath}/following-sibling::"
            "*[@data-testid='field-widgets-extra-button']"
        )

    # field

    def do_place_caret_after(self, text: str) -> None:
        """
        Places the caret right after the first occurrence of `text` in the
        field. A real click cannot target a character reliably.
        """
        field = self.test_case.find_element(self.field_xpath, by=By.XPATH)
        found = self.test_case.execute_script(
            """
            const [field, text] = arguments;
            field.focus();
            const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT);
            while (walker.nextNode()) {
              const node = walker.currentNode;
              const index = node.nodeValue.indexOf(text);
              if (index !== -1) {
                window.getSelection().collapse(node, index + text.length);
                return true;
              }
            }
            return false;
            """,
            field,
            text,
        )
        assert found, f"Text not found in the field: {text!r}"

    def do_place_caret_on_next_line(self, text: str) -> None:
        """
        Places the caret at the start of the line that follows `text`.
        `text` must end its line.
        """
        self.do_place_caret_after(text)
        self.do_type_at_caret(Keys.ARROW_RIGHT)

    # The caret has no element, so the scripts below put an empty marker
    # element at the caret, use it, remove it, and restore the caret.
    CARET_MARKER_SCRIPT = """
        const selection = window.getSelection();
        const range = selection.getRangeAt(0);
        const [node, offset] = [range.startContainer, range.startOffset];
        const marker = document.createElement('span');
        range.insertNode(marker);
        const result = (%s)(marker);
        marker.remove();
        selection.collapse(node, offset);
        return result;
    """

    def do_add_space_above_field(self) -> None:
        """
        A short document does not scroll. An empty element at the start of
        the scroll container of the field makes it scroll, so the field can
        be scrolled up to the bottom of the viewport.
        """
        field = self.test_case.find_element(self.field_xpath, by=By.XPATH)
        self.test_case.execute_script(
            """
            let container = arguments[0].parentElement;
            while (container &&
              !/(auto|scroll)/.test(getComputedStyle(container).overflowY)) {
              container = container.parentElement;
            }
            const space = document.createElement('div');
            space.style.minHeight = `${2 * window.innerHeight}px`;
            (container ?? document.body).prepend(space);
            """,
            field,
        )

    def do_scroll_caret_to_viewport_bottom(self) -> None:
        self.test_case.execute_script(
            self.CARET_MARKER_SCRIPT % "(marker) => marker.scrollIntoView("
            "{block: 'end', behavior: 'instant'})"
        )

    def wait_for_caret_in_viewport(self, timeout: float = 5) -> None:
        """
        The caret must be inside the visible area of the scroll container
        of the field, which ends above the page footer. The page scrolls
        smoothly, so the caret gets there with a delay.
        """

        def caret_in_viewport(_) -> bool:
            return self.test_case.execute_script(
                self.CARET_MARKER_SCRIPT
                % """(marker) => {
                    let container = marker.parentElement;
                    while (container && !/(auto|scroll)/.test(
                      getComputedStyle(container).overflowY)) {
                      container = container.parentElement;
                    }
                    const area = container ?
                      container.getBoundingClientRect() :
                      {top: 0, bottom: window.innerHeight};
                    const rect = marker.getBoundingClientRect();
                    return rect.top >= area.top && rect.bottom <= area.bottom;
                }"""
            )

        WebDriverWait(self.test_case.driver, timeout).until(caret_in_viewport)

    def do_paste_at_caret(self, text: str) -> None:
        """
        Pastes the text as the browser would on Ctrl+V, with a paste event
        that carries the text. A real Ctrl+V needs the system clipboard.
        """
        field = self.test_case.find_element(self.field_xpath, by=By.XPATH)
        self.test_case.execute_script(
            """
            const [field, text] = arguments;
            const data = new DataTransfer();
            data.setData('text/plain', text);
            field.dispatchEvent(new ClipboardEvent('paste', {
              clipboardData: data,
              bubbles: true,
              cancelable: true,
            }));
            """,
            field,
            text,
        )

    def do_type_at_caret(self, text: str) -> None:
        ActionChains(self.test_case.driver).send_keys(text).perform()

    # The browser's undo and redo keys: Ctrl+Z and Ctrl+Shift+Z, Cmd on macOS.
    UNDO_MODIFIER = (
        Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
    )

    def do_undo(self) -> None:
        ActionChains(self.test_case.driver).key_down(
            self.UNDO_MODIFIER
        ).send_keys("z").key_up(self.UNDO_MODIFIER).perform()

    def do_redo(self) -> None:
        ActionChains(self.test_case.driver).key_down(
            self.UNDO_MODIFIER
        ).key_down(Keys.SHIFT).send_keys("z").key_up(Keys.SHIFT).key_up(
            self.UNDO_MODIFIER
        ).perform()

    def get_field_text(self) -> str:
        field = self.test_case.find_element(self.field_xpath, by=By.XPATH)
        return self.test_case.execute_script(
            "return arguments[0].innerText;", field
        )

    def wait_for_field_text(self, text: str, timeout: float = 5) -> None:
        """
        For changes that come after a caret move: the browser reports the
        move with a delay (selectionchange).
        """
        WebDriverWait(self.test_case.driver, timeout).until(
            lambda _: self.get_field_text() == text
        )

    def assert_field_text(self, text: str) -> None:
        field = self.test_case.find_element(self.field_xpath, by=By.XPATH)
        actual = self.test_case.execute_script(
            "return arguments[0].innerText;", field
        )
        assert actual == text, f"{actual!r} != {text!r}"

    # button

    def assert_button(self, mode: str) -> None:
        """`mode` is "insert" or "edit"."""
        self.test_case.assert_element(
            f"{self.button_xpath}[@data-mode='{mode}']", by=By.XPATH
        )

    def assert_button_hidden(self) -> None:
        self.test_case.assert_element_not_visible(
            self.button_xpath, by=By.XPATH
        )

    def assert_extra_button(self, title: str) -> None:
        self.test_case.assert_element(
            f"{self.extra_button_xpath}[@title='{title}']", by=By.XPATH
        )

    def assert_extra_button_hidden(self) -> None:
        self.test_case.assert_element_not_visible(
            self.extra_button_xpath, by=By.XPATH
        )

    def do_click_extra_button(self) -> None:
        self.test_case.click_xpath(self.extra_button_xpath)

    def do_open_insert_menu(self) -> None:
        self.assert_button("insert")
        self.test_case.click_xpath(self.button_xpath)
        self.assert_insert_menu_open()

    # insert menu

    def assert_insert_menu_open(self) -> None:
        self.test_case.assert_element(self.INSERT_MENU, by=By.XPATH)
        self.test_case.assert_element(
            f"{self.field_xpath}{self.PLACEHOLDER}", by=By.XPATH
        )

    def assert_insert_menu_closed(self) -> None:
        self.test_case.assert_element_not_present(self.INSERT_MENU, by=By.XPATH)
        self.test_case.assert_element_not_present(self.PLACEHOLDER, by=By.XPATH)

    def assert_insert_items(self, widget_ids: List[str]) -> None:
        """The visible items of the insert menu, in order."""
        actual = self.test_case.execute_script(
            """
            return [...document.querySelectorAll(arguments[0])]
              .filter((item) => !item.hidden)
              .map((item) => item.dataset.testid);
            """,
            "[data-testid='field-widgets-insert-menu'] "
            "[js-field_widgets-insert]",
        )
        expected = [f"field-widgets-insert-{id_}" for id_ in widget_ids]
        assert actual == expected, f"{actual!r} != {expected!r}"

    def assert_on_top(self, xpath: str) -> None:
        """
        Nothing covers the center of the element, for example a modal. A
        click does not prove it: SeleniumBase falls back to a script click.
        """
        element = self.test_case.find_element(xpath, by=By.XPATH)
        on_top = self.test_case.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            const top = document.elementFromPoint(
              rect.left + rect.width / 2, rect.top + rect.height / 2);
            return arguments[0].contains(top);
            """,
            element,
        )
        assert on_top, f"Element is covered: {xpath}"

    def do_close_insert_menu_by_escape(self) -> None:
        ActionChains(self.test_case.driver).send_keys(Keys.ESCAPE).perform()
        self.assert_insert_menu_closed()

    def do_close_insert_menu_by_click(self) -> None:
        self.test_case.click_xpath(
            f"{self.INSERT_MENU}//*[@data-testid='field-widgets-menu-close']"
        )
        self.assert_insert_menu_closed()

    def do_choose_insert_item(self, widget_id: str) -> None:
        self.test_case.click_xpath(
            f"{self.INSERT_MENU}"
            f"//*[@data-testid='field-widgets-insert-{widget_id}']"
        )
        self.assert_insert_menu_closed()

    def do_choose_insert_item_by_enter(self) -> None:
        ActionChains(self.test_case.driver).send_keys(Keys.ENTER).perform()
        self.assert_insert_menu_closed()
