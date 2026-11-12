from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import BaseCase


class FieldWidgets:  # pylint: disable=invalid-name
    """
    The field widgets of a multiline form field: the caret, the field's
    button, and the insert menu.
    """

    INSERT_MENU = "//*[@data-testid='field-widgets-insert-menu']"

    def __init__(self, test_case: BaseCase, field_name: str) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(field_name, str)
        self.test_case: BaseCase = test_case
        self.field_xpath = f"//*[@data-testid='form-field-{field_name}']"
        self.button_xpath = (
            f"{self.field_xpath}/following-sibling::"
            "*[@data-testid='field-widgets-button']"
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

    def do_type_at_caret(self, text: str) -> None:
        ActionChains(self.test_case.driver).send_keys(text).perform()

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

    def do_open_insert_menu(self) -> None:
        self.assert_button("insert")
        self.test_case.click_xpath(self.button_xpath)
        self.test_case.assert_element(self.INSERT_MENU, by=By.XPATH)

    def do_close_insert_menu_by_escape(self) -> None:
        ActionChains(self.test_case.driver).send_keys(Keys.ESCAPE).perform()
        self.test_case.assert_element_not_present(self.INSERT_MENU, by=By.XPATH)

    def do_choose_insert_item(self, widget_id: str) -> None:
        self.test_case.click_xpath(
            f"{self.INSERT_MENU}"
            f"//*[@data-testid='field-widgets-insert-{widget_id}']"
        )
