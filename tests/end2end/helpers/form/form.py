# pylint: disable=invalid-name
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from strictdoc.helpers.mid import MID
from tests.end2end.e2e_case import E2ECase


class Form:  # pylint: disable=invalid-name
    def __init__(self, test_case: E2ECase) -> None:
        assert isinstance(test_case, E2ECase)
        self.test_case: E2ECase = test_case

    #
    # Base.
    #

    def assert_on_form(self) -> None:
        self.test_case.assert_element(
            "//sdoc-form",
            by=By.XPATH,
        )

    def assert_on_modal(self) -> None:
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )

    #
    # Assert field content.
    #

    def assert_error(self, message: str) -> None:
        self.test_case.assert_element(
            f"//sdoc-form-error[contains(., '{message}')]", by=By.XPATH
        )

    def assert_contenteditable_contains(self, text: str) -> None:
        self.test_case.assert_element(
            f"//sdoc-contenteditable[contains(., '{text}')]", by=By.XPATH
        )

    def assert_xpath_contains(self, xpath: str, text: str) -> None:
        self.test_case.assert_element(
            f"{xpath}[contains(., '{text}')]", by=By.XPATH
        )

    def assert_testid_contains(self, testid: str, text: str) -> None:
        self.test_case.assert_element(
            f"//*[@{testid}][contains(., '{text}')]", by=By.XPATH
        )

    #
    # Open TAB.
    #

    def do_open_tab(self, tab_name: str = "") -> None:
        assert isinstance(tab_name, str)
        self.test_case.click_xpath(f"//*[@data-testid='form-tab-{tab_name}']")
        # should have the attribute
        self.test_case.assert_attribute(
            f"//*[@data-testid='form-tab-{tab_name}']",
            "active",
            "",
            by=By.XPATH,
        )

    def assert_tab_is_open(self, tab_name: str = "") -> None:
        assert isinstance(tab_name, str)
        # should have the attribute
        self.test_case.assert_attribute(
            f"//*[@data-testid='form-tab-{tab_name}']",
            "active",
            "",
            by=By.XPATH,
        )

    #
    # Work with fields containers.
    #

    # TODO: update with mid
    def do_delete_field(self, field_name: str, field_order: int = 1) -> None:
        assert isinstance(field_name, str)
        self.test_case.click_xpath(
            f"(//*[@data-testid='form-delete-field-action-{field_name}'])"
            f"[{field_order}]"
        )

    #
    # MOVE fields.
    #

    def do_move_field_up(self, mid: MID, test_id: str) -> None:
        assert isinstance(mid, MID)
        self.test_case.click_xpath(
            f"(//*[@mid='{mid}' and @data-testid='{test_id}'])"
        )

    def do_move_field_down(self, field_name: str = "") -> None:
        assert isinstance(field_name, str)
        self.test_case.click_xpath(
            f"(//*[@data-testid='form-move-down-{field_name}-field-action'])"
        )

    #
    # Work with fields content.
    #

    def do_fill_in(
        self, field_name: str, field_value: str, field_order: int = 1
    ) -> None:
        assert isinstance(field_name, str)
        assert isinstance(field_value, str)

        field_order_str = "last()" if field_order == -1 else str(field_order)

        self.test_case.type(
            (
                f"(//*[@data-testid='form-field-{field_name}'])"
                f"[{field_order_str}]"
            ),
            f"{field_value}",
            by=By.XPATH,
        )

    def do_fill_in_mid(self, mid: MID, test_id: str, field_value: str) -> None:
        assert isinstance(mid, MID)
        assert isinstance(test_id, str)
        assert isinstance(field_value, str)

        field_xpath = f"(//*[@mid='{mid}' and @data-testid='{test_id}'])"
        for _ in range(3):
            self.test_case.type(field_xpath, f"{field_value}", by=By.XPATH)
            element = self.test_case.find_element(field_xpath)
            if element.text == field_value:
                break
        else:
            raise AssertionError(
                f"The text field could not be filled with the value: "
                f"'{field_value}'."
            )

    def do_use_first_autocomplete_result(
        self, test_id: str, field_value: str
    ) -> None:
        assert isinstance(test_id, str)
        assert isinstance(field_value, str)

        field_xpath = f"(//*[@data-testid='{test_id}'])"
        element = self.test_case.find_element(field_xpath)
        hidden_input = element.find_element(
            By.XPATH, 'following-sibling::input[@type="hidden"]'
        )
        results_ul = hidden_input.find_element(
            By.XPATH, "following-sibling::ul[1]"
        )

        # We simulate a user typing the supplied field_value.
        self.test_case.type(field_xpath, f"{field_value}", by=By.XPATH)

        # We wait until the results <ul> is displayed.
        WebDriverWait(self.test_case.driver, 3).until(
            lambda _: results_ul.is_displayed()
        )

        # We send Arrow-Down and Enter select the first match.
        # The stimulus.js controller uses a debounce of 10ms, we are
        # careful to use an larger interval inbetween key presses.
        len_before_autocomplete = len(element.text.lower().strip())
        select_first_match_action = ActionChains(self.test_case.driver)
        select_first_match_action.send_keys(Keys.ARROW_DOWN).pause(
            0.1
        ).send_keys(Keys.RETURN).perform()

        # Now wait for the length of the field to increase, this means
        # the autocomplete did happen.
        WebDriverWait(self.test_case.driver, timeout=3).until(
            lambda _: (
                len(element.text.lower().strip()) > len_before_autocomplete
            )
        )

    def do_append_command_and_use_autocomplete_result_again(
        self, test_id: str, field_value: str
    ) -> None:
        assert isinstance(test_id, str)
        assert isinstance(field_value, str)

        field_xpath = f"(//*[@data-testid='{test_id}'])"
        element = self.test_case.find_element(field_xpath)
        hidden_input = element.find_element(
            By.XPATH, 'following-sibling::input[@type="hidden"]'
        )
        results_ul = hidden_input.find_element(
            By.XPATH, "following-sibling::ul[1]"
        )

        # We simulate a user typing a comma, and the supplied field_value.
        element.send_keys(f",{field_value}")

        # We wait until the results <ul> is displayed.
        WebDriverWait(self.test_case.driver, 3).until(
            lambda _: results_ul.is_displayed()
        )

        # We send Arrow-Down and Enter select the first match.
        # The stimulus.js controller uses a debounce of 50ms, we are
        # careful to use an larger interval inbetween key presses.
        len_before_autocomplete = len(element.text.lower().strip())
        select_first_match_action = ActionChains(self.test_case.driver)
        select_first_match_action.send_keys(Keys.ARROW_DOWN).pause(
            0.1
        ).send_keys(Keys.RETURN).perform()

        # Now wait for the length of the field to increase, this means
        # the autocomplete did happen.
        WebDriverWait(self.test_case.driver, timeout=3).until(
            lambda _: (
                len(element.text.lower().strip()) > len_before_autocomplete
            )
        )

    def do_use_first_autocomplete_result_mid(
        self, mid: MID, test_id: str, field_value: str
    ) -> None:
        assert isinstance(mid, MID)
        assert isinstance(test_id, str)
        assert isinstance(field_value, str)

        field_xpath = f"(//*[@mid='{mid}' and @data-testid='{test_id}'])"
        for _ in range(3):
            self.test_case.type(field_xpath, f"{field_value}", by=By.XPATH)
            element = self.test_case.find_element(field_xpath)
            element.send_keys(Keys.ARROW_DOWN)
            element.send_keys(Keys.RETURN)
            if field_value in element.text:
                break
        else:
            raise AssertionError(
                f"The text field could not be filled with the value: "
                f"'{field_value}'."
            )

    def do_clear_field(self, field_name: str, field_order: int = 1) -> None:
        assert isinstance(field_name, str)
        # HACK: The only way the field is actually cleared.
        self.test_case.type(
            f"(//*[@data-testid='form-field-{field_name}'])[{field_order}]",
            "1",
            by=By.XPATH,
        )
        this_field = self.test_case.find_visible_elements(
            f"//*[@data-testid='form-field-{field_name}']"
        )[0]
        # FIXME:
        # https://github.com/strictdoc-project/strictdoc/actions/runs/7402267894/job/20139782839?pr=1567
        this_field.send_keys(Keys.BACKSPACE)
        this_field.send_keys(Keys.BACKSPACE)
        this_field.send_keys(Keys.BACKSPACE)

    #
    # Save/Cancel.
    #

    def do_form_cancel(self) -> None:
        self.test_case.click_xpath('//*[@data-testid="form-cancel-action"]')
        self.test_case.assert_element_not_present(
            '//*[@data-testid="form-cancel-action"]'
        )

    def do_form_submit(self) -> None:
        self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')
        self.test_case.assert_element_not_present(
            '//*[@data-testid="form-submit-action"]'
        )

    def do_form_submit_and_catch_error(self, message: str) -> None:
        self.test_case.click_xpath('//*[@data-testid="form-submit-action"]')
        self.test_case.assert_element(
            "//sdoc-form-error",
            by=By.XPATH,
        )
        self.test_case.assert_text(f"{message}")
