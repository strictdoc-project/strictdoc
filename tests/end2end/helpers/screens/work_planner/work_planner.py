from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)


class Screen_WorkPlanner:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="work-planner"]',
            by=By.XPATH,
        )
        self.test_case.wait_for_ready_state_complete()
        self.test_case.assert_no_js_errors()

    def assert_contains_text(self, text: str) -> None:
        self.test_case.assert_text(text)

    def do_open_add_epic_form(self) -> Form_EditRequirement:
        self.test_case.click_xpath(
            "(//a[@data-work-planner-add-template"
            " and contains(@data-work-planner-add-template, 'element_type=EPIC')])[1]"
        )
        form = Form_EditRequirement(self.test_case)
        form.assert_on_modal()
        form.assert_on_form()
        return form

    def get_canvas_scroll_left(self) -> int:
        return int(
            self.test_case.execute_script(
                "return document.querySelector('[data-work-planner-canvas-scroll]').scrollLeft;"
            )
        )

    def do_pan_canvas_to_the_right(self) -> None:
        canvas = self.test_case.find_element(
            "[data-work-planner-canvas-scroll]",
            by=By.CSS_SELECTOR,
        )
        ActionChains(self.test_case.driver).move_to_element_with_offset(
            canvas, 120, 40
        ).key_down(Keys.SPACE).click_and_hold().move_by_offset(
            -240, 0
        ).release().key_up(Keys.SPACE).perform()
