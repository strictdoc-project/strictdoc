from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import BaseCase


class Modal:  # pylint: disable=invalid-name  # noqa: E501
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    # base actions

    @staticmethod
    def get(test_case: BaseCase) -> "Modal":
        assert isinstance(test_case, BaseCase)
        return Modal(test_case=test_case)

    def assert_not_modal(self) -> None:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)

    def assert_modal(self) -> None:
        self.test_case.assert_element("//sdoc-modal", by=By.XPATH)

    def assert_in_modal(self, xpath: str) -> None:
        assert isinstance(xpath, str)
        self.test_case.assert_element(
            f"//sdoc-modal{xpath}",
            by=By.XPATH,
        )

    def do_close_modal(self) -> None:
        """Uses Escape key. Includes assert_not_modal."""
        self.test_case.get_element("html").send_keys(Keys.ESCAPE)
        self.assert_not_modal()

    def do_close_modal_with_button(self) -> None:
        """Uses Close button. Includes assert_not_modal."""
        self.test_case.click(
            selector=('//sdoc-modal//*[@data-testid="form-cancel-action"]'),
            by=By.XPATH,
        )
        self.assert_not_modal()
