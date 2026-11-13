from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.end2end.helpers.components.field_widgets import FieldWidgets


class AnchorWidget(FieldWidgets):  # pylint: disable=invalid-name
    """
    The anchor widget of a multiline form field: the form with the UID and
    the title of a new anchor.
    """

    FORM = "//*[@data-testid='field-widgets-anchor-form']"
    UID_INPUT = f"{FORM}//*[@data-testid='field-widgets-anchor-uid']"
    UID_MESSAGE = f"{FORM}//*[@data-testid='field-widgets-anchor-uid-message']"
    TITLE_INPUT = f"{FORM}//*[@data-testid='field-widgets-anchor-title']"
    TITLE_MESSAGE = (
        f"{FORM}//*[@data-testid='field-widgets-anchor-title-message']"
    )
    INSERT_BUTTON = f"{FORM}//*[@data-testid='field-widgets-anchor-insert']"

    def do_open_form(self) -> None:
        self.do_open_insert_menu()
        self.do_choose_insert_item("anchor")
        self.test_case.assert_element(self.FORM, by=By.XPATH)

    def do_type_uid(self, uid: str) -> None:
        self.test_case.type(self.UID_INPUT, uid, by=By.XPATH)

    def do_type_title(self, title: str) -> None:
        self.test_case.type(self.TITLE_INPUT, title, by=By.XPATH)

    def assert_uid_message(self, text: str) -> None:
        """
        The server check of the UID comes with a delay.
        """
        self.test_case.assert_text(text, self.UID_MESSAGE, by=By.XPATH)

    def assert_title_message(self, text: str) -> None:
        self.test_case.assert_text(text, self.TITLE_MESSAGE, by=By.XPATH)

    def assert_insert_enabled(self) -> None:
        self.test_case.wait_for_element_clickable(
            self.INSERT_BUTTON, by=By.XPATH
        )

    def assert_insert_disabled(self) -> None:
        button = self.test_case.find_element(self.INSERT_BUTTON, by=By.XPATH)
        assert not button.is_enabled()

    def do_click_insert(self) -> None:
        self.test_case.click_xpath(self.INSERT_BUTTON)
        self.test_case.assert_element_not_present(self.FORM, by=By.XPATH)

    def do_insert_by_enter(self) -> None:
        ActionChains(self.test_case.driver).send_keys(Keys.ENTER).perform()
        self.test_case.assert_element_not_present(self.FORM, by=By.XPATH)

    def do_close_form_by_escape(self) -> None:
        ActionChains(self.test_case.driver).send_keys(Keys.ESCAPE).perform()
        self.test_case.assert_element_not_present(self.FORM, by=By.XPATH)
