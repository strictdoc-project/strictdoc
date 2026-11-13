from typing import List

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from tests.end2end.helpers.components.field_widgets import FieldWidgets


class LinkWidget(FieldWidgets):  # pylint: disable=invalid-name
    """
    The link widget of a multiline form field: the popup of link targets at
    the caret.
    """

    POPUP = "//*[@data-testid='field-widgets-link-popup']"

    def _option_xpath(self, uid: str) -> str:
        return f"{self.POPUP}//*[@data-autocompletable-value='{uid}']"

    def wait_for_options(self, uids: List[str], timeout: float = 5) -> None:
        """
        The popup loads the options with a delay after the last keystroke.
        """

        def options(_) -> List[str]:
            return self.test_case.execute_script(
                """
                return [...document.querySelectorAll(arguments[0])]
                  .map((option) => option.dataset.autocompletableValue);
                """,
                "[data-testid='field-widgets-link-popup'] "
                "[data-autocompletable-value]",
            )

        WebDriverWait(self.test_case.driver, timeout).until(
            lambda driver: options(driver) == uids
        )

    def wait_for_popup_closed(self, timeout: float = 5) -> None:
        """
        The popup closes after the response to the last query.
        """
        WebDriverWait(self.test_case.driver, timeout).until(
            lambda driver: not driver.find_elements(By.XPATH, self.POPUP)
        )

    def assert_popup_closed(self) -> None:
        self.test_case.assert_element_not_present(self.POPUP, by=By.XPATH)

    def do_choose_by_enter(self) -> None:
        ActionChains(self.test_case.driver).send_keys(Keys.ENTER).perform()
        self.assert_popup_closed()

    def do_choose_by_click(self, uid: str) -> None:
        self.test_case.click_xpath(self._option_xpath(uid))
        self.assert_popup_closed()

    def do_close_popup_by_escape(self) -> None:
        ActionChains(self.test_case.driver).send_keys(Keys.ESCAPE).perform()
        self.assert_popup_closed()
